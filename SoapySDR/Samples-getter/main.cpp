#include <iostream>
#include <fstream>
#include <SoapySDR/Device.hpp>
#include <SoapySDR/Formats.hpp>

void listDevices(const SoapySDR::KwargsList & s_results);
SoapySDR::Device * getRTLSDR(const SoapySDR::KwargsList & s_results);
void getDeviceInfo(const SoapySDR::Device * s_device);
void saveStream(SoapySDR::Device * s_device, double s_sample_rate, double s_frequency, 
                const std::string & s_amp_name, double s_gain, 
                int s_samples_amount = 1000, 
                const std::string & s_filename = "output.wav",
                size_t s_channel = 1);

int main() {

    constexpr double SAMPLE_RATE {2.048e+06};
    constexpr double FREQUENCY {100e+06};
    constexpr const char * AMP_DEVICE {"TUNER"};
    constexpr double GAIN_VALUE {27.2};

    //Getting a list of SDR devices available for operation
    SoapySDR::KwargsList results {SoapySDR::Device::enumerate()};
    listDevices(results);
    SoapySDR::Device * rtlsdr {getRTLSDR(results)};
    getDeviceInfo(rtlsdr);
    saveStream(rtlsdr, SAMPLE_RATE, FREQUENCY, AMP_DEVICE, GAIN_VALUE);

    return 0;

}

void listDevices(const SoapySDR::KwargsList & s_results) {

    std::cout << std::endl << "Available devices: " << std::endl;
    for (SoapySDR::Kwargs i : s_results) {
        for (SoapySDR::Kwargs::iterator it {i.begin()}; it != i.end(); ++it)
            std::cout << it -> first << ": " << it -> second << std::endl;
        std::cout << std::endl;
    }

}
SoapySDR::Device * getRTLSDR(const SoapySDR::KwargsList & s_results) {

    for (SoapySDR::Kwargs i : s_results) {
        for (SoapySDR::Kwargs::iterator it {i.begin()}; it != i.end(); ++it) {
            if (it -> first == "driver")
                if (it -> second == "rtlsdr")
                    return SoapySDR::Device::make(i);
        }
    }

}
void getDeviceInfo(const SoapySDR::Device * s_device) {
    
    std::cout << "Get device info: " << std::endl;

    size_t channel {s_device -> getNumChannels(SOAPY_SDR_RX)};
    std::cout << "Channels amount: " << channel << std::endl;
    
    std::cout << "Samples rates: " << std::endl;
    for (auto i : s_device -> listSampleRates(SOAPY_SDR_RX, channel))
        std::cout << "    " << i << std::endl;
    
    std::cout << "RX gains list: " << std::endl;
    for (auto i : s_device -> listGains(SOAPY_SDR_RX, channel))
        std::cout << "    " << i << ": " << 
        s_device -> getGainRange(SOAPY_SDR_RX, channel, i).minimum() << " - " <<
        s_device -> getGainRange(SOAPY_SDR_RX, channel, i).maximum() << std::endl;
    
    std::cout << "Frequencies names and ranges: " << std::endl;
    for (auto i : s_device -> listFrequencies(SOAPY_SDR_RX, channel)) {
        std::cout << "    " << i << ": ";
        auto freq_range {s_device -> getFrequencyRange(SOAPY_SDR_RX, channel, i)};
        std::cout << freq_range.front().minimum() << " - " << freq_range.back().maximum() << std::endl;
    }

    std::cout << std::endl;

}
void saveStream(SoapySDR::Device * s_device, double s_sample_rate, double s_frequency, 
                const std::string & s_amp_name, double s_gain, 
                int s_samples_amount, const std::string & s_filename, size_t s_channel){
    
    s_device -> setSampleRate(SOAPY_SDR_RX, s_channel, s_sample_rate);
    s_device -> setFrequency(SOAPY_SDR_RX, s_channel, s_frequency);
    //Disabling AGC mode
    s_device -> setGainMode(SOAPY_SDR_RX, s_channel, false);
    s_device -> setGain(SOAPY_SDR_RX, s_channel, s_amp_name, s_gain);
    //Initializing a stream with data of type complex float32 (8 bytes per element)
    SoapySDR::Stream * rx_stream {s_device -> setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)};

    s_device -> activateStream(rx_stream);
    //Getting the size of one data block
    size_t size {s_device -> getStreamMTU(rx_stream)};
    //Buffer for storing the complex component of the signal
    std::complex<float> buffer[size];
    //Creating a file to save output I + Q data
    std::ofstream file {s_filename, std::ios_base::binary};
    
    for (int i {0}; i < s_samples_amount; ++i) {
        void * buf[] {buffer};
        int flags;
        long long time_ns;
        
        int ret {s_device -> readStream(rx_stream, buf, size, flags, time_ns)};
        
        std::cout << "ret = " << ret << ", "      //Number of items read or error code
                  << "flags = "  << flags << ", " //Results flags
                  << " time (ns) = " << time_ns   //Buffer timestamp in nanoseconds 
                  << std::endl;
        
        file.write(reinterpret_cast<const char*>(buffer), sizeof(std::complex<float>) * size);
    }

    s_device -> deactivateStream(rx_stream);
    s_device -> closeStream(rx_stream);

    SoapySDR::Device::unmake(s_device);

}