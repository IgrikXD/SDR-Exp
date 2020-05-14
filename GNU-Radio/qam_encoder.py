#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: QAM-Encoder
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
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from grc_gnuradio import blks2 as grc_blks2
from optparse import OptionParser
import osmosdr
import pmt
import sip
import sys
import time
from gnuradio import qtgui


class qam_encoder(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "QAM-Encoder")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("QAM-Encoder")
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

        self.settings = Qt.QSettings("GNU Radio", "qam_encoder")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.center_freq = center_freq = 145.75e6
        self.lo_freq = lo_freq = 80e3
        self.freq = freq = center_freq
        self.samp_rate = samp_rate = 8e6
        self.rf_gain = rf_gain = 0
        self.qpsk = qpsk = digital.constellation_rect(([0.707+0.707j, -0.707+0.707j, -0.707-0.707j, 0.707-0.707j]), ([0, 1, 2, 3]), 4, 2, 2, 1, 1).base()
        self.if_gain = if_gain = 20
        self.data_freq = data_freq = freq+lo_freq

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
        self._if_gain_range = Range(0, 47, 1, 20, 200)
        self._if_gain_win = RangeWidget(self._if_gain_range, self.set_if_gain, 'IF Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._if_gain_win)
        self.rational_resampler_xxx_0_1 = filter.rational_resampler_ccc(
                interpolation=32,
                decimation=1,
                taps=None,
                fractional_bw=None,
        )
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=10,
                decimation=1,
                taps=None,
                fractional_bw=None,
        )
        self.qtgui_sink_x_0 = qtgui.sink_c(
        	1024, #fftsize
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	center_freq, #fc
        	samp_rate/32, #bw
        	"", #name
        	True, #plotfreq
        	True, #plotwaterfall
        	True, #plottime
        	True, #plotconst
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_sink_x_0_win)

        self.qtgui_sink_x_0.enable_rf_freq(True)



        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + 'hackrf=0000000000000000a27466e62362050f' )
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(center_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(rf_gain, 0)
        self.osmosdr_sink_0.set_if_gain(if_gain, 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self._freq_tool_bar = Qt.QToolBar(self)

        if None:
          self._freq_formatter = None
        else:
          self._freq_formatter = lambda x: eng_notation.num_to_str(x)

        self._freq_tool_bar.addWidget(Qt.QLabel('Center frequency'+": "))
        self._freq_label = Qt.QLabel(str(self._freq_formatter(self.freq)))
        self._freq_tool_bar.addWidget(self._freq_label)
        self.top_grid_layout.addWidget(self._freq_tool_bar)
        self.digital_qam_mod_0 = digital.qam.qam_mod(
          constellation_points=4,
          mod_code="gray",
          differential=True,
          samples_per_symbol=4,
          excess_bw=0.35,
          verbose=False,
          log=False,
          )
        self._data_freq_tool_bar = Qt.QToolBar(self)

        if None:
          self._data_freq_formatter = None
        else:
          self._data_freq_formatter = lambda x: eng_notation.num_to_str(x)

        self._data_freq_tool_bar.addWidget(Qt.QLabel('Data center frequency'+": "))
        self._data_freq_label = Qt.QLabel(str(self._data_freq_formatter(self.data_freq)))
        self._data_freq_tool_bar.addWidget(self._data_freq_label)
        self.top_grid_layout.addWidget(self._data_freq_tool_bar)
        self.blocks_throttle_1 = blocks.throttle(gr.sizeof_char*1, 25000,True)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, 'D:\\Input-data.txt', True)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blks2_packet_encoder_0 = grc_blks2.packet_mod_b(grc_blks2.packet_encoder(
        		samples_per_symbol=4,
        		bits_per_symbol=4,
        		preamble='',
        		access_code='',
        		pad_for_usrp=True,
        	),
        	payload_length=0,
        )
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate/32, analog.GR_COS_WAVE, lo_freq, 1, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blks2_packet_encoder_0, 0), (self.digital_qam_mod_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle_1, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.rational_resampler_xxx_0_1, 0))
        self.connect((self.blocks_throttle_1, 0), (self.blks2_packet_encoder_0, 0))
        self.connect((self.digital_qam_mod_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.rational_resampler_xxx_0_1, 0), (self.osmosdr_sink_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "qam_encoder")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.qtgui_sink_x_0.set_frequency_range(self.center_freq, self.samp_rate/32)
        self.osmosdr_sink_0.set_center_freq(self.center_freq, 0)
        self.set_freq(self._freq_formatter(self.center_freq))

    def get_lo_freq(self):
        return self.lo_freq

    def set_lo_freq(self, lo_freq):
        self.lo_freq = lo_freq
        self.set_data_freq(self._data_freq_formatter(self.freq+self.lo_freq))
        self.analog_sig_source_x_0.set_frequency(self.lo_freq)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        Qt.QMetaObject.invokeMethod(self._freq_label, "setText", Qt.Q_ARG("QString", self.freq))
        self.set_data_freq(self._data_freq_formatter(self.freq+self.lo_freq))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_sink_x_0.set_frequency_range(self.center_freq, self.samp_rate/32)
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate/32)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self._rf_gain_callback(self.rf_gain)
        self.osmosdr_sink_0.set_gain(self.rf_gain, 0)

    def get_qpsk(self):
        return self.qpsk

    def set_qpsk(self, qpsk):
        self.qpsk = qpsk

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_sink_0.set_if_gain(self.if_gain, 0)

    def get_data_freq(self):
        return self.data_freq

    def set_data_freq(self, data_freq):
        self.data_freq = data_freq
        Qt.QMetaObject.invokeMethod(self._data_freq_label, "setText", Qt.Q_ARG("QString", self.data_freq))


def main(top_block_cls=qam_encoder, options=None):

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
