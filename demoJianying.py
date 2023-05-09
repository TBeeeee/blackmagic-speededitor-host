#!/usr/bin/env python3

# Copyright (C) 2021 Sylvain Munaut <tnt@246tNt.com>
# SPDX-License-Identifier: Apache-2.0
import keyboard

from typing import List

from bmd import SpeedEditorKey, SpeedEditorLed, SpeedEditorJogLed, SpeedEditorJogMode, SpeedEditorHandler, SpeedEditor

class DemoHandler(SpeedEditorHandler):

	JOG = {
		SpeedEditorKey.SHTL:	( SpeedEditorJogLed.SHTL, SpeedEditorJogMode.RELATIVE_2 ),
		SpeedEditorKey.JOG:		( SpeedEditorJogLed.JOG,  SpeedEditorJogMode.ABSOLUTE_CONTINUOUS ),
		SpeedEditorKey.SCRL:	( SpeedEditorJogLed.SCRL, SpeedEditorJogMode.ABSOLUTE_DEADZERO ),
	}

	# Shortcut Keys for JianyingPro Using FCPX preform
	ShortcutKeys = {
		SpeedEditorKey.IN : ("I",None),			#selectRangeStart
		SpeedEditorKey.OUT : ("O",None),			#selectRangeEnd
		SpeedEditorKey.SNAP :       ("N",SpeedEditorLed.SNAP),	#adsorb

		SpeedEditorKey.LIVE_OWR :  ("S",None),	#preview
		SpeedEditorKey.STOP_PLAY : ("Space",None),#togglePlay
		SpeedEditorKey.FULL_VIEW :("ctrl+shift+f",None),#toggleFullscreen
		SpeedEditorKey.SMTH_CUT :("ctrl+b",None),		#cutoff No need to toggle the LED
		SpeedEditorKey.CUT :("b",SpeedEditorLed.CUT,"a"),		#toggle the mouse mode or cut mode
		# use different method to handle the wheel
		#SpeedEditorKey.JOG_UP:("Right",""),	#nextFrame
		#SpeedEditorKey.JOG_DOWN:("Left",""),	#prevFrame
	}

	def __init__(self, se):
		self.se   = se
		self.keys = []
		self.leds = 0
		self.summation = 0
		self.limit_rate = 5
		self.counter = 0
		self.se.set_leds(self.leds)
		self._set_jog_mode_for_key(SpeedEditorKey.SHTL)

	def _set_jog_mode_for_key(self, key : SpeedEditorKey):
		if key not in self.JOG:
			return
		self.se.set_jog_leds( self.JOG[key][0] )
		self.se.set_jog_mode( self.JOG[key][1] )
		self.summation = 0

	def accumulator(self, num, mode : SpeedEditorJogMode):
		if num == "clear":
			self.summation = 0 
			return  None
		try:
			num = int(num)
		except ValueError:
			return "Error: parameter must be a number." 
		#if not hasattr(self, 'sum'): # check if the attribute sum exists for the accumulator function
		#    self.summation = num	     # if it doesn't exist, set it to 0
		if abs(num) > 3500 and mode != 2:
			self.summation += num	      # add the current number to the sum
			self.se.set_jog_mode( mode )
		return self.summation + num

	def jog(self, mode : SpeedEditorJogMode, value):
		valued = self.accumulator( value, mode )
		# self.se.set_jog_mode( mode )
		# print(f"Jog mode {mode:d} : {value:d} : {self.summation:d}")
		print(f"Jog mode {mode:d} : {valued:d}")
		self.counter += 1
		if self.counter == self.limit_rate:
			if valued > 0 :
				keyboard.send("right")
			else:
				keyboard.send("left")
			self.counter = 0

	def key(self, keys : List[SpeedEditorKey]):
		# Debug message
		kl = ', '.join([k.name for k in keys])
		flip = 0
		if not kl:
			kl = 'None'
		for key in keys:
			if key in self.ShortcutKeys:
				if self.ShortcutKeys[key][1] is not None:
					if self.leds & getattr(SpeedEditorLed, key.name, 0) != 0 and len(self.ShortcutKeys[key]) == 3:
						flip = 2
					self.leds ^= getattr(SpeedEditorLed, key.name, 0)
					# print(ori_value,self.leds)
					self.se.set_leds(self.leds)
				keyboard.send(self.ShortcutKeys[key][flip])
		print(f"Keys held: {kl:s}")
		#  Press ESC key to exit the demo program
		if kl == 'ESC':
			exit()
		# Find keys being released and toggle led if there is one
		# for k in self.keys:
		# 	if k not in keys:
		# 		# Select jog mode
		# 		self._set_jog_mode_for_key(k)
        # 
		# 		# Toggle leds
		# 		self.leds ^= getattr(SpeedEditorLed, k.name, 0)
		# 		self.se.set_leds(self.leds)

		self.keys = keys

	def __del__(self):
		self.leds = 0
		self.se.set_leds( self.leds )
		self.se.set_jog_leds( SpeedEditorJogLed.NONE )
		self.se.close_handler()
		print("exit the program")

	def battery(self, charging : bool, level : int):
		print(f"Battery {level:d} %{' and charging' if charging else '':s}")


if __name__ == '__main__':
	se = SpeedEditor()
	se.authenticate()
	se.set_handler(DemoHandler(se))

	while True:
		se.poll(3)
