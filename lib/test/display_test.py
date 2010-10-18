import lib.display

class TestDisplay:
	def setup(self):
		self.display = lib.display.Display()

	def test_display_decodes_gt_entity(self):
		assert self.display.html_decode("&gt;") == '>'

	def test_html_decode_doesnt_remove_single_ampersand(self):
		assert self.display.html_decode("&;") == '&;'

	def test_html_decode_doesnt_replace_unprintable_entites(self):
		unprintable_entity = "&Ouml;"
		assert self.display.html_decode(unprintable_entity) == unprintable_entity
