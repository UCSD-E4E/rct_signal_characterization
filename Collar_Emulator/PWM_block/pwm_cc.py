#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import time
import numpy
from gnuradio import gr
from decimal import Decimal

class pwm_cc(gr.sync_block):
    """
    docstring for block pwm_cc
    """
    def __init__(self,secs,secs1):
	global var
        var=time.time() #Global var saves the time program executed
	gr.sync_block.__init__(self,
            name="pwm_cc",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
	self.secs = secs #High Time
	self.secs1 = secs1 #Off Time
	print self.secs
	print self.secs1

    def work(self, input_items, output_items):
	count=float("{0:.3f}".format(time.time()-var)) # get current time-start time in order to use mod
	count=Decimal(count)  #Uses Decimal class in order to use modulos (%) in the loop
	x=1
	i=0.00
	while i<self.secs:
		if float("{0:.2f}".format(count%Decimal(self.secs1+i)))==0.0: #checks if part of High time
			x=0
			output_items[0][:]=input_items[0] #lets incoming signal pass through the block
			return len(output_items[0])	
		i=i+0.01
	if x==1: #if not part of High time
		output_items[0][:]=0 #outputs 0 (no signal pass through)
	return len(output_items[0])

