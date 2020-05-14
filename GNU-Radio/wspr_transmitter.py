#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: WSPR-Transmitter
# Author: Ihar Yatsevich
# GNU Radio version: 3.7.13.5
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import osmosdr
import sys
import time
from gnuradio import qtgui


class wspr_transmitter(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "WSPR-Transmitter")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("WSPR-Transmitter")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "wspr_transmitter")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.center_freq = center_freq = 50.293e6
        self.samp_rate = samp_rate = 8e6
        self.rf_gain = rf_gain = 0
        self.ppm_cor = ppm_cor = 0
        self.lo_freq = lo_freq = 10e3
        self.if_gain = if_gain = 20
        self.data_freq_0 = data_freq_0 = center_freq
        self.data_freq = data_freq = center_freq+1500
        self.audio_rate = audio_rate = 48000

        ##################################################
        # Blocks
        ##################################################
        _rf_gain_check_box = Qt.QCheckBox('RF Gain enable')
        self._rf_gain_choices = {True: 14, False: 0}
        self._rf_gain_choices_inv = dict((v,k) for k,v in self._rf_gain_choices.iteritems())
        self._rf_gain_callback = lambda i: Qt.QMetaObject.invokeMethod(_rf_gain_check_box, "setChecked", Qt.Q_ARG("bool", self._rf_gain_choices_inv[i]))
        self._rf_gain_callback(self.rf_gain)
        _rf_gain_check_box.stateChanged.connect(lambda i: self.set_rf_gain(self._rf_gain_choices[bool(i)]))
        self.top_grid_layout.addWidget(_rf_gain_check_box)
        self._ppm_cor_range = Range(-3, 3, 0.1, 0, 200)
        self._ppm_cor_win = RangeWidget(self._ppm_cor_range, self.set_ppm_cor, 'PPM Correction', "counter_slider", float)
        self.top_grid_layout.addWidget(self._ppm_cor_win)
        self._if_gain_range = Range(0, 47, 1, 20, 200)
        self._if_gain_win = RangeWidget(self._if_gain_range, self.set_if_gain, 'IF Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._if_gain_win)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=500,
                decimation=3,
                taps=None,
                fractional_bw=None,
        )
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + 'hackrf=0000000000000000a27466e62362050f' )
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(center_freq-lo_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(ppm_cor, 0)
        self.osmosdr_sink_0.set_gain(rf_gain, 0)
        self.osmosdr_sink_0.set_if_gain(if_gain, 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self._data_freq_0_tool_bar = Qt.QToolBar(self)

        if None:
          self._data_freq_0_formatter = None
        else:
          self._data_freq_0_formatter = lambda x: eng_notation.num_to_str(x)

        self._data_freq_0_tool_bar.addWidget(Qt.QLabel('Set receiver frequency in USB mode'+": "))
        self._data_freq_0_label = Qt.QLabel(str(self._data_freq_0_formatter(self.data_freq_0)))
        self._data_freq_0_tool_bar.addWidget(self._data_freq_0_label)
        self.top_grid_layout.addWidget(self._data_freq_0_tool_bar)
        self._data_freq_tool_bar = Qt.QToolBar(self)

        if None:
          self._data_freq_formatter = None
        else:
          self._data_freq_formatter = lambda x: eng_notation.num_to_str(x)

        self._data_freq_tool_bar.addWidget(Qt.QLabel('WSPR data center frequency'+": "))
        self._data_freq_label = Qt.QLabel(str(self._data_freq_formatter(self.data_freq)))
        self._data_freq_tool_bar.addWidget(self._data_freq_label)
        self.top_grid_layout.addWidget(self._data_freq_tool_bar)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('D:\\WSPR.wav', False)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.band_pass_filter_0 = filter.fir_filter_ccf(1, firdes.band_pass(
        	1, audio_rate, lo_freq+1e3, lo_freq+2e3, 250, firdes.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0 = analog.sig_source_c(audio_rate, analog.GR_COS_WAVE, lo_freq, 0.5, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.osmosdr_sink_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "wspr_transmitter")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.osmosdr_sink_0.set_center_freq(self.center_freq-self.lo_freq, 0)
        self.set_data_freq_0(self._data_freq_0_formatter(self.center_freq))
        self.set_data_freq(self._data_freq_formatter(self.center_freq+1500))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self._rf_gain_callback(self.rf_gain)
        self.osmosdr_sink_0.set_gain(self.rf_gain, 0)

    def get_ppm_cor(self):
        return self.ppm_cor

    def set_ppm_cor(self, ppm_cor):
        self.ppm_cor = ppm_cor
        self.osmosdr_sink_0.set_freq_corr(self.ppm_cor, 0)

    def get_lo_freq(self):
        return self.lo_freq

    def set_lo_freq(self, lo_freq):
        self.lo_freq = lo_freq
        self.osmosdr_sink_0.set_center_freq(self.center_freq-self.lo_freq, 0)
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.audio_rate, self.lo_freq+1e3, self.lo_freq+2e3, 250, firdes.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0.set_frequency(self.lo_freq)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_sink_0.set_if_gain(self.if_gain, 0)

    def get_data_freq_0(self):
        return self.data_freq_0

    def set_data_freq_0(self, data_freq_0):
        self.data_freq_0 = data_freq_0
        Qt.QMetaObject.invokeMethod(self._data_freq_0_label, "setText", Qt.Q_ARG("QString", self.data_freq_0))

    def get_data_freq(self):
        return self.data_freq

    def set_data_freq(self, data_freq):
        self.data_freq = data_freq
        Qt.QMetaObject.invokeMethod(self._data_freq_label, "setText", Qt.Q_ARG("QString", self.data_freq))

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.audio_rate, self.lo_freq+1e3, self.lo_freq+2e3, 250, firdes.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0.set_sampling_freq(self.audio_rate)


def main(top_block_cls=wspr_transmitter, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
