import csv
import folium
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
import base64
from folium import plugins
from folium.plugins import Draw, MeasureControl, Search
from streamlit_folium import st_folium
from st_on_hover_tabs import on_hover_tabs
import time
import plotly.express as px
from PIL import Image
import unicodedata
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title='Catalogue of Neo-Assyrian Toponyms 2', page_icon='resources/icon/icon.png', layout='wide')  # change favicon and page title

# load cuneiform fonts
def load_font_css(font_name, font_path):
	with open(font_path, "rb") as f:
		font_data = f.read()
		b64_font = base64.b64encode(font_data).decode()
		return f"""
		@font-face {{
			font-family: '{font_name}';
			src: url(data:font/ttf;base64,{b64_font}) format('truetype');
		}}
		"""
fonts_css = ""
fonts_css += load_font_css("Linux Libertine Display", "resources/fonts/LinLibertine_DRah.ttf")
fonts_css += load_font_css("Assurbanipal", "resources/fonts/Assurbanipal.ttf")

st.markdown(f"<style>{fonts_css}</style>", unsafe_allow_html=True)  # insert fonts into the app page

image = Image.open('resources/images/CNAT3.png')
st.sidebar.image(image)
st.sidebar.write('<b><font style="font-size: 1.3em"><br><br></font></b>', unsafe_allow_html=True)

# sidebar tabs
#st.markdown('<style>' + open('resources/tabStyle/style.css').read() + '</style>', unsafe_allow_html=True)
with st.sidebar:
	tabs = on_hover_tabs(tabName=['Catalogue', 'About', 'References', 'Statistics', 'Downloads'], iconName=['search', 'home', 'menu_book', 'bar_chart', 'download'],
		styles = {'navtab': {'background-color':'#262730',
			'color': '#ababab',
			'font-size': '17px',
			'transition': '.3s',
			'white-space': 'nowrap',
			'text-transform': 'uppercase'},
		'tabStyle': {':hover :hover': {'color': 'red', 'cursor': 'pointer'}},
		'tabStyle' : {'list-style-type': 'none',
			'margin-bottom': '30px',
			'padding-left': '5px'},
		'iconStyle':{'position':'fixed',
			'left':'5px',
			'text-align': 'left'},
		},
		default_choice=0, key="1")

def clearSearchForm():
	st.session_state['44481919633371111725'] = ''
	st.session_state['44481919633223337725'] = ''
	st.session_state['44481914496333772335578'] = ''
	st.session_state['44481559196443337725'] = ''
	st.session_state['4448155919644333772558'] = ''

def customAlphabetSort(sortedDF, sortedColumn):
	customAlphabet = list(' .–-0₀1₁2₂3₃4₄5₅6₆7₇8₈9₉ʾ’ʿ‘`AaĀāÂâÁáÀàÄäBbCcÇçDdḌḍḎḏEeĒēÉéÊêÈèËëFfGgĞğǦǧHhḪḫḤḥIiĪīÎîÍíÌìİıÏïJjKkLlMmNnOoŌōÔôÓóÖöPpQqRrŘřSsṢṣŞşŠšTtṬṭŢţṮṯUuŪūÛûÚúÙùÜüVvWwXxYyZz!"#$%_()*+,/:;<=>?@[]^&{|}~')
	lowercaseAlphabet = [char.lower() for char in customAlphabet]
	charOrder = {char: i for i, char in enumerate(lowercaseAlphabet)}
	baseVowels = {'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'}
	def normalizeText(text):
		normalized = []
		for char in str(text):
			lowerChar = char.lower()
			decomposed = unicodedata.normalize('NFKD', lowerChar)
			baseChar = decomposed[0] if len(decomposed) > 0 else lowerChar
			if baseChar in baseVowels:
				normalized.append(baseChar)
			else:
				normalized.append(lowerChar)
		return ''.join(normalized)
	def sortKey(word):
		normalized = normalizeText(word)
		return [charOrder.get(char, len(customAlphabet)) for char in normalized]
	sortedDF = sortedDF.sort_values(by=sortedColumn, key=lambda x: x.map(sortKey))
	return sortedDF

if tabs == 'Catalogue':
	st.write('<b><font style="font-family: Linux Libertine Display, sans-serif; font-size: 2.1em">CATALOGUE</font></b>', unsafe_allow_html=True)
	st.write('<b><font style="font-size: 25px">Search</font></b> (case insensitive, regular expressions allowed):', unsafe_allow_html=True)

	data2 = pd.read_csv('resources/data/AssyrianProject-AllNoDupl.csv', usecols=['name', 'altName', 'cer', 'lat', 'lon', 'writ', 'type', 'countr', 'ha', 'bibl', 'order'])
	data1 = customAlphabetSort(data2, 'name')

	col1, col2, col3, col4, col5 = st.columns([9, 9, 9, 9, 9])
	with col1:
		locName = st.text_input('Ancient or modern name:', key=44481919633371111725, label_visibility='visible')
	with col2:
		locWritten = st.text_input('Written form:', key=44481919633223337725, label_visibility='visible')
	with col3:
		locType = st.text_input('Type:', key=44481914496333772335578, label_visibility='visible')
	with col4:
		locCountry = st.text_input('Country or territory:', key=44481559196443337725, label_visibility='visible')
	with col5:
		locBibliography = st.text_input('Bibliography:', key=4448155919644333772558, label_visibility='visible')

	with col5:
		clearSearchForm = st.button('Clear form', key='clearSearchForm', on_click=clearSearchForm, use_container_width=True)  # clear form

	if locName != '':
		foundName = data1.loc[data1['altName'].str.contains(locName, case=False, regex=True, na=False)]
	else:
		foundName = data1

	if locWritten != '':
		foundWritten = foundName.loc[foundName['writ'].str.contains(locWritten, case=False, regex=True, na=False)]
	else:
		foundWritten = foundName

	if locType != '':
		foundType = foundWritten.loc[foundWritten['type'].str.contains(locType, case=False, regex=True, na=False)]
	else:
		foundType = foundWritten

	if locCountry != '':
		foundCountry = foundType.loc[foundType['countr'].str.contains(locCountry, case=False, regex=True, na=False)]
	else:
		foundCountry = foundType

	if locBibliography != '':
		data = foundCountry.loc[foundCountry['bibl'].str.contains(locBibliography, case=False, regex=True, na=False)]
	else:
		data = foundCountry

	# style of columns
	cellsytle_jscode = JsCode(
		"""
	function(params) {
		if (params.value != '–') {
			return {
				'color': 'white',
				'backgroundColor': '#0E1117',
				'font-size':'1.3em',
			}
		} else {
			return {
				'color': 'white',
				'backgroundColor': '#262730',
				'font-size':'1.3em',
			}
		}
	};
	"""
	)

	# style of the map
	st.markdown("""
		<style>
		[title~="st.iframe"] { width: 100%}
		</style>
	""", unsafe_allow_html=True)

	# customize aggrid
	gb = GridOptionsBuilder.from_dataframe(data)
	gb.configure_side_bar()
	gb.configure_default_column(
		editable=False,
		resizable=True,
		sorteable=True, 
		autoHeight=False,
		headerComponentParams={
			"template":
				'<div class="ag-cell-label-container" role="presentation">' +
				'  <span ref="eMenu" class="ag-header-icon ag-header-cell-menu-button"></span>' +
				'  <div ref="eLabel" class="ag-header-cell-label" role="presentation">' +
				'    <span ref="eSortOrder" class="ag-header-icon ag-sort-order"></span>' +
				'    <span ref="eSortAsc" class="ag-header-icon ag-sort-ascending-icon"></span>' +
				'    <span ref="eSortDesc" class="ag-header-icon ag-sort-descending-icon"></span>' +
				'    <span ref="eSortNone" class="ag-header-icon ag-sort-none-icon"></span>' +
				'    <span ref="eText" class="ag-header-cell-text" role="columnheader" style="font-size: 1.3em; text-align: right;"></span>' +
				'    <span ref="eFilter" class="ag-header-icon ag-filter-icon"></span>' +
				'  </div>' +
				'</div>'
		}
	)
	gb.configure_selection('', use_checkbox=True, groupSelectsChildren='Group checkbox select children')
	gb.configure_column('order', headerName='ID', maxWidth=90, minWidth=85, cellStyle=cellsytle_jscode)
	gb.configure_column('name', headerName='Name', cellStyle={'color': '#ffffab', 'font-weight': 'bold', 'backgroundColor': '#0E1117', 'font-size':'1.3em'})
	gb.configure_column('altName', headerName='All names', cellStyle=cellsytle_jscode)
	gb.configure_column('cer', headerName='c.', maxWidth=35, minWidth=25, cellStyle=cellsytle_jscode)
	gb.configure_column('lat', headerName='Latitude', cellStyle=cellsytle_jscode)
	gb.configure_column('lon', headerName='Longitude', cellStyle=cellsytle_jscode)
	gb.configure_columns('writ', headerName='Written forms', cellStyle={'fontFamily': 'sans-serif, Assurbanipal', 'color': 'white', 'backgroundColor': '#0E1117', 'font-size':'1.2em'})
	gb.configure_column('type', headerName='Type', cellStyle=cellsytle_jscode)
	gb.configure_column('countr', headerName='Country or territory', cellStyle=cellsytle_jscode)
	gb.configure_column('ha', hide=True)
	gb.configure_column('bibl', headerName='Bibliography', cellStyle=cellsytle_jscode)
	gridOptions = gb.build()

	with st.expander('', expanded=True):
		st.write('Catalogue contains ', data1['name'].count(), 'toponyms, found', data['name'].count(), 'item(s).')
		grid_response = AgGrid(
			data,
			allow_unsafe_jscode=True,
			gridOptions=gridOptions,
			DataReturnMode='AS_INPUT',
			GridUpdateMode='MODEL_CHANGED',
			fit_columns_on_grid_load=True,
			theme='streamlit',  # themes: streamlit, light, dark/balham, blue, fresh, material
			enable_enterprise_modules=False,
			height=300, 
			width='100%',
			reload_data=False
		)

		data = grid_response['data']
		selected = grid_response['selected_rows'] 
		df1 = pd.DataFrame(selected)

	with st.expander('', expanded=True):
		if len(df1.columns) != 0:
			for index, row in df1.iterrows():
				st.write('<font color="#0AA43A" size="6"><b>', row['name'], '</b></font>', unsafe_allow_html=True)
				row['altName'] = row['altName'].replace(', ', '<br>')
				row['writ'] = row['writ'].replace(', ', '<br>')
				row['type'] = row['type'].replace(', ', '<br>')
				row['countr'] = row['countr'].replace(', ', '<br>')
				row['bibl'] = row['bibl'].replace(', ', '<br>')
				c1, c2 = st.columns([5, 7])
				with c1:
					st.write('<table border=0 width="100%" style="font-family: sans-serif; font-size: 1.1em"><tr><td width="40%" style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font color="#b0b0b0"><b>All names:</b></font></td><td width="60%" style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['altName'], 
						'</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font color="#b0b0b0"><b>Written form(s):</b></font></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', '<font style="font-family: sans-serif, Assurbanipal; font-size: 1.1em">', row['writ'], '</font>', 
						'</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font color="#b0b0b0"><b>Type:</b></font></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['type'], 
						'</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font color="#b0b0b0"><b>Country:</b></font></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['countr'], 
						'</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font color="#b0b0b0"><b>Coordinates:</b></font></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['lat'], ', ', row['lon'], 
						'</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font color="#b0b0b0"><b>Certainty:</b></font></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['cer'], 
						'</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font color="#b0b0b0"><b>Bibliography:</b></font></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['bibl'], '</td></tr></table>', unsafe_allow_html=True)
				with c2:
					map4 = folium.Map(
						location=[36.01821343935203, 49.93455352210664],
						tiles=None,
						zoom_start=5,
					)

					folium.TileLayer(name='OpenStreetMap', attr="Data by © <a href='https://www.openstreetmap.org/#map=8/49.817/15.478'>OpenStreetMap</a>, under <a href='https://www.openstreetmap.org/copyright'>ODbL</a>", show=True).add_to(map4)
					folium.TileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png', name='OpenStreetMap (DE)', attr="Daten © <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</code>-Mitwirkende (<a href='https://opendatacommons.org/licenses/odbl/index.html'>ODbL</a>), <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, <a href='https://openstreetmap.org/fixthemap'>mitmachen/Fehler melden</a>", show=False).add_to(map4)
					folium.TileLayer('http://cawm.lib.uiowa.edu/tiles/{z}/{x}/{y}.png', name='CAWM Tile Server', attr="Data by <a href='http://cawm.lib.uiowa.edu/index.html' target='_blank'>Consortium of Ancient World Mappers</a> (under <a href='https://creativecommons.org/licenses/by/4.0/' target='_blank'>CC BY 4.0</a>)", show=False).add_to(map4)
					folium.TileLayer('https://tile.opentopomap.org/{z}/{x}/{y}.png', name='OpenTopoMap', attr="Kartendaten: © <a href='https://www.openstreetmap.org/copyright' target='_blank'>OpenStreetMap</a>-Mitwirkende, SRTM | Kartendarstellung: © <a href='https://opentopomap.org/#map=7/35.572/40.210' target='_blank'>OpenTopoMap</a> (<a href='https://creativecommons.org/licenses/by-sa/3.0/' target='_blank'>CC-BY-SA</a>)", show=False).add_to(map4)

					tooltip = '<b>' + row['name'] + '</b>'

					plugins.Fullscreen(position='topleft',
						title='Full screen ON', 
						title_cancel='Full screen OFF',
						force_separate_button=True).add_to(map4)

					df2 = df1[df1['lat'] != '–']
					if len(df2) != 0:
						folium.Marker([row['lat'], row['lon']], tooltip=tooltip, icon=folium.Icon(color='red', icon='none')).add_to(map4)
						folium.LayerControl(position='bottomleft').add_to(map4)
						st_data = st_folium(map4, height=810, use_container_width=True)
					else:
						folium.LayerControl(position='bottomleft').add_to(map4)
						st_data = st_folium(map4, height=810, use_container_width=True)
						st.markdown('<font style="color:#FF4B4B"><b>Coordinates unknown or unavailable.</b></font>', unsafe_allow_html=True)
		else:
			st.write('')

elif tabs == 'About':
	c1, c2, c3 = st.columns([1, 17, 1], gap='small')
	with c2:
		st.write('<b><font style="font-family: Linux Libertine Display, sans-serif; font-size: 2.1em">ABOUT</font></b>', unsafe_allow_html=True)
		st.write('<br>', unsafe_allow_html=True)
		st.write(
			"""
			<font style="font-size: 1.3em">The <i>Catalogue of Neo-Assyrian Toponyms 2</i> provides another interface for data from my <a href="https://cnat.zcu.cz/catalog" target="_blank">Catalog of Neo-Assyrian Toponyms</a>. The older interface (although helpful and pretty) was created and provided “as is” and is quite complex, so I also need a less elaborate and more flexible solution for some purposes now. The data is (and will be) the same in both catalogues.

			This project primarily collects information on ancient Near Eastern sites known from Assyrian texts dated to the 1<sup>st</sup> half of the 1<sup>st</sup> millennium BCE, i.e., to the Neo-Assyrian period. However, some notable sites from other periods also appear in the collection. <a href="http://home.zcu.cz/~ksaskova/map/AncientNearEast.html" target="_blank">The map of the ancient Near East: Tukultī-Ninurta II 885 BCE</a> shows toponyms with known coordinates from this catalogue.

			Data on particular locations is collected and processed by <a href="https://zcu.academia.edu/Kate%C5%99ina%C5%A0a%C5%A1kov%C3%A1" target="_blank">Kateřina Šašková</a> with contributions from Christopher W. Jones, Nathan Nuulimba and Maija Holappa. See also the <i>References</i> section.

			Please note that the catalogue is still under development and some information may be inaccurate and/or incomplete. For an overview of recent changes, see the <i>Statistics</i> section.</font>""", unsafe_allow_html=True)

elif tabs == 'References':
	c1, c2, c3 = st.columns([1, 17, 1], gap='small')
	with c2:
		st.write('<b><font style="font-family: Linux Libertine Display, sans-serif; font-size: 2.1em">REFERENCES</font></b>', unsafe_allow_html=True)
		st.write(
	"""
	### **Maps and localities**
	<font style="font-size: 1.3em">

	‣ Åhlfeldt, Johan, 2020: *Digital Atlas of the Roman Empire (DARE)*. http://imperium.ahlfeldt.se/.

	‣ Anastasio, S., Lebeau, M., Sauvage, M., 2004: *Atlas of Preclassical Upper Mesopotamia*. Subartu XIII. Turnhout: Brepols Publishers.

	‣ *Archival Texts of the Assyrian Empire (ATAE)*. http://oracc.museum.upenn.edu/atae/.
	
	‣ Bagg, A. M., 2007: *Die Orts- und Gewässernamen der neuassyrischen Zeit. Die Levante*. RGTC 7/1. Wiesbaden: Dr. Ludwig Reichert Verlag.

	‣ Bagg, A. M., 2017: *Die Orts- und Gewässernamen der neuassyrischen Zeit. Zentralassyrien und benachbarte Gebiete, Ägypten und die arabische Halbinsel*. RGTC 7/2. Wiesbaden: Dr. Ludwig Reichert Verlag.

	‣ Bagg, A. M., 2020: *Die Orts- und Gewässernamen der neuassyrischen Zeit. Babylonien, Urarṭu und die östlichen Gebiete*. RGTC 7/3. Wiesbaden: Dr. Ludwig Reichert Verlag.

	‣ Brughmans, T., de Soto, P., Pažout, A. and Bjerregaard Vahlstrup, P., 2024: *Itiner-e: the digital atlas of ancient roads*. https://itiner-e.org/.

	‣ Cancik-Kirschbaum, E., Hess, Ch., 2017: *Toponyme der mittelassyrischen Texte: Der Westen des mittelassyrischen Reiches. Obermesopotamien im 2. Jt. v.Chr*. MTT I/2. Paris: Collège de France, SEPOA. DOI: https://doi.org/10.4000/books.cdf.4439 (https://books.openedition.org/cdf/4439).

	‣ *CDLI: Proveniences*. https://cdli.mpiwg-berlin.mpg.de/proveniences/.

	‣ *The Digital Archaeological Atlas of the Holy Land (DAAHL)*. https://daahl.ucsd.edu/DAAHL/Home.php.

	‣ Fink, Ch., 2017: *Fundorte und Karten. Obermesopotamien im 2. Jt. v.Chr.* MTT I/3. Paris: Collège de France, SEPOA. DOI: https://doi.org/10.4000/books.cdf.4487 (https://books.openedition.org/cdf/4487).

	‣ *GeoNames*. https://www.geonames.org/.

	‣ de Graauw, A., 2022: *Ancient Ports and Harbours, The Catalogue*. 8th ed. Grenoble. pdf downloadable from A. de Graauw, *Ancient Ports – Ports antiques*, website: http://www.ancientportsantiques.com/docs-pdf/, catalogue: https://www.ancientportsantiques.com/the-catalogue/.

	‣ Grayson, A. K., 1975: *Assyrian and Babylonian Chronicles*. New York: J. J. Augustin Publisher.

	‣ Holappa, Maija: *Helsinki Atlas Sites + CIGS*. https://www.google.com/maps/d/u/0/viewer?mid=1XWivnuuHzEfy0BJ6nMOdRbkLojLzahA&ll.

	‣ *OpenStreetMap*. https://www.openstreetmap.org/.

	‣ Parpola, S., 1970: *Neo-Assyrian Toponyms*. Neukirchen-Vluyn: Neukirchener Verlag – Verlag Butzon & Bercker Kevelaer.

	‣ Parpola, S., Porter, M. (eds.), 2001: *The Helsinki Atlas of the Near East in the Neo-Assyrian Period*. Helsinki: The Neo-Assyrian Text Corpus Project – The Casco Bay Assyriological Institute.

	‣ Pedersén, O. *ANE Placemarks for Google Earth*. https://www.lingfil.uu.se/research/assyriology/earth/.

	‣ Pedersén, O. *Water Placemarks for Google Earth*. https://www.uu.se/en/department/linguistics-and-philology/research/proj/geographic-data-near-east.

	‣ *Pleiades*. https://pleiades.stoa.org/.

	‣ Postgate, J. N., 1995: Assyria: The Home Provinces. In M. Liverani (ed.), *Neo-Assyrian Geography*. Roma: Università di Roma, 1–17.

	‣ Radner, K., 2006: *Provinz. C. Assyrien*. RlA 11, 42–68.

	‣ Rattenborg, R., Johansson, C., Nett, S., Smidt, G. R., Andersson, J. 2021: *Cuneiform Inscriptions Geographical Site Index (CIGS)*. DOI: https://doi.org/10.5281/zenodo.5217600 (https://zenodo.org/record/5217600).

	‣ *Reallexikon der Assyriologie und vorderasiatischen Archäologie (RlA)*. Berlin – Leipzig: De Gruyter, 1928–2018. https://publikationen.badw.de/de/rla/index.

	‣ *The Royal Inscriptions of Assyria online (RIAo) Project*. http://oracc.museum.upenn.edu/riao/.

	‣ *The Royal Inscriptions of the Neo-Assyrian Period (RINAP)*. http://oracc.museum.upenn.edu/rinap/.

	‣ de Soto, P. et al., 2025: *A High-Resolution Dataset of Roads of the Roman Empire: Itiner-e static version 2024*. Zenodo. https://doi.org/10.5281/zenodo.17122148.

	‣ *State Archives of Assyria Online (SAAo)*. http://oracc.museum.upenn.edu/saao/.

	‣ Talbert, Richard J. A. (ed.), 2000: *Barrington Atlas of the Greek and Roman World*. Princeton: Princeton University Press.

	‣ *Textual Sources of the Assyrian Empire (TSAE)*. https://oracc.museum.upenn.edu/tsae/index.html.

	‣ Titolo, A., Palmisano, A., 2025: *UnitoAssyrianGovernance/villages-to-empire-dataset: Paper submission version (1.0)*. DOI: https://doi.org/10.5281/zenodo.15111789.

	‣ *Trismegistos: An interdisciplinary portal of the ancient world*. Leuven: KU Leuven. https://www.trismegistos.org.

	‣ *Vici.org*. https://vici.org/.

	‣ Zadok, R., 1985: *Geographical names according to New- and Late-Babylonian texts*. RGTC 8. Wiesbaden: Dr. Ludwig Reichert Verlag.

	‣ Ziegler, N., Langlois, A.-I., 2017: *Les toponymes paléo-babyloniens de la Haute-Mésopotamie. La Haute-Mésopotamie au IIe millénaire av. J.-C.* MTT I/1. Paris: Collège de France, SEPOA. DOI: https://doi.org/10.4000/books.cdf.4393 (https://books.openedition.org/cdf/4393).

	### <br>**Cuneiform fonts**

	‣ *Assurbanipal.ttf* created by Sylvie Vanséveren, available at the Hethitologie Portal Mainz. https://www.hethport.uni-wuerzburg.de/cuneifont/.

	‣ *CuneiformComposite.ttf* created by Steve Tinney, available at The Open Richly Annotated Cuneiform Corpus website. http://oracc.museum.upenn.edu/doc/help/visitingoracc/fonts/.

	‣ *Old Babylonian Freie* created by Corvin R. Ziegeler, available at https://refubium.fu-berlin.de/handle/fub188/45271 and https://github.com/crzfub/OB-Freie.

	‣ *Santakku.ttf* created by Sylvie Vanséveren, available at the Hethitologie Portal Mainz. https://www.hethport.uni-wuerzburg.de/cuneifont/.

	‣ *SantakkuM.ttf* created by Sylvie Vanséveren, available at the Hethitologie Portal Mainz. https://www.hethport.uni-wuerzburg.de/cuneifont/.

	‣ *Sinacherib.ttf* created by Kateřina Šašková, available at http://home.zcu.cz/~ksaskova/.

	### <br>**Guides and tools**

	‣ Crymble, A., 2015: *Using Gazetteers to Extract Sets of Keywords from Free-Flowing Texts*. Programming Historian 4. https://programminghistorian.org/en/lessons/extracting-keywords.

	‣ *Folium documentation*. https://python-visualization.github.io/folium/.
	
	‣ *Geojson.io*. http://geojson.io.

	‣ *Google Maps*. https://www.google.com/maps.

	‣ *QGIS. A Free and Open Source Geographic Information System*. https://www.qgis.org/en/site/.

	‣ Sharma, A., 2020. *Your Guide to Getting Started with Geospatial Analysis using Folium (with multiple case studies)*. https://www.analyticsvidhya.com/blog/2020/06/guide-geospatial-analysis-folium-python/.

	‣ *Streamlit documentation*. https://docs.streamlit.io/.
	</font>""", unsafe_allow_html=True)

elif tabs == 'Statistics':
	st.write('<b><font style="font-family: Linux Libertine Display, sans-serif; font-size: 2.1em">STATISTICS</font></b>', unsafe_allow_html=True)

	newEditedDeleted = pd.read_csv('resources/data/000-newEditedDeleted.csv')
	newEditedDeleted.sort_values('appended', ascending=False, inplace=True)
	newEditedDeleted['appended'] = newEditedDeleted['appended'].str.replace('-(', ' (')
	newEditedDeleted['appended'] = newEditedDeleted['appended'].str.replace(')', '):')

	with st.expander('', expanded=True):
		st.write('<b><font style="font-size: 1.5em; color: #ffffab">Recent changes</font></b>', unsafe_allow_html=True)

		def listRecentChanges(countX, rangeX):
			x = countX
			c1, c2, c3 = st.columns([8.7, 2.9, 10.3], gap='small')
			with c1:
				st.write('<b><font style="font-size: 1.1em">Date:</font></b>', unsafe_allow_html=True)
			with c2:
				st.write('<b><font style="font-size: 1.1em">State:</font></b>', unsafe_allow_html=True)
			with c3:
				st.write('<b><font style="font-size: 1.1em">Name and ID:</font></b>', unsafe_allow_html=True)

			for entry in range(rangeX):
				with c1:
					st.write(x+1, '<font style="font-size: 1em">', newEditedDeleted['appended'].iloc[x], '</font>', unsafe_allow_html=True)
				with c2:
					if newEditedDeleted['state'].iloc[x] == 'edited':
						st.write('<font style="font-size: 1em; color: #de7604">', newEditedDeleted['state'].iloc[x], '</font>', unsafe_allow_html=True)
					elif newEditedDeleted['state'].iloc[x] == 'deleted':
						st.write('<font style="font-size: 1em; color: #f51d0a">', newEditedDeleted['state'].iloc[x], '</font>', unsafe_allow_html=True)
					else:
						st.write('<font style="font-size: 1em; color: #02d12f">', newEditedDeleted['state'].iloc[x], '</font>', unsafe_allow_html=True)
				with c3:
					st.write('<b><font style="font-size: 1em; color: #ffffab">', newEditedDeleted['title'].iloc[x], '</font></b> <font style="font-size: 1em"> (ID: ', str(newEditedDeleted['order'].iloc[x]), ')</font>', unsafe_allow_html=True)
				x = x+1

		windowSize = streamlit_js_eval(js_expressions='[window.innerWidth, window.innerHeight]', key='windowSize')
		if windowSize:
			width, height = windowSize
			if width < 768:
				listRecentChanges(0, 60)
			elif width < 1350:
				colum1, colum2, colum3 = st.columns([15, 3, 15], gap='small')
				with colum1:
					listRecentChanges(0, 30)
				with colum3:
					listRecentChanges(30, 30)
			else:
				colum1, colum2, colum3, colum4, colum5 = st.columns([15, 0.3, 15, 0.3, 15], gap='small')
				with colum1:
					listRecentChanges(0, 20)
				with colum3:
					listRecentChanges(20, 20)
				with colum5:
					listRecentChanges(40, 20)

	localitiesCSV = pd.read_csv('resources/data/AssyrianProject-AllNoDupl.csv')
	localities = pd.DataFrame(localitiesCSV)
	localities = customAlphabetSort(localities, 'name')
	localities.rename(columns=({'order': 'ID', 'name': 'Name', 'altName': 'All names', 'cer': 'Certainty', 'writ': 'Written forms', 'type': 'Type', 'countr': 'Country or territory', 'ha': 'Helsinki Atlas map and grid', 'bibl': 'Bibliography'}), inplace=True)
	localitiesCoord = localities[localities['lat'] != '–']

	with st.expander('', expanded=True):
		st.write('<b><font style="font-size: 1.5em; color: #ffffab">All localities </font><br><font style="font-size: 1.1em">Count: ', localities['ID'].count(), '</font></b>', unsafe_allow_html=True)
		st.dataframe(localities, use_container_width=True, hide_index=True)

	with st.expander('', expanded=True):
		st.write('<b><font style="font-size: 1.5em; color: #ffffab">Localities with coordinates </font><br><font style="font-size: 1.1em">Count: ', localitiesCoord['ID'].count(), '</font></b>', unsafe_allow_html=True)
		st.dataframe(localitiesCoord, use_container_width=True, hide_index=True)

	with st.expander('', expanded=True):
		st.write('<b><font style="font-size: 1.5em; color: #ffffab">Geographical distribution</font></b>', unsafe_allow_html=True)
		localitiesLatLon = pd.DataFrame(localitiesCoord, columns=['lat', 'lon'])
		localitiesLatLon['lat'] = localitiesLatLon['lat'].astype(float)
		localitiesLatLon['lon'] = localitiesLatLon['lon'].astype(float)
		st.map(localitiesLatLon, use_container_width=True)

	with st.expander('', expanded=True):
		st.write('<b><font style="font-size: 1.5em; color: #ffffab">Some other statistics</font></b>', unsafe_allow_html=True)
		localities.rename(columns=({'lat': 'Latitude', 'lon': 'Longitude'}), inplace=True)
		c1, c2 = st.columns([3, 3], gap='small')
		with c1:
			plotBy = st.selectbox('Plot by', ('Type', 'Country or territory', 'Certainty', 'Helsinki Atlas map and grid'), key='plotBy')
		with c2:
			pieHeigth1 = st.slider('Chart size', 300, 1500, 750, key='pieHeigth1')

		localities7 = pd.DataFrame(localities[plotBy].value_counts()).head(50)
		localities9 = localities7
		localities9.columns=['Count']
		localities9[plotBy] = localities9.index

		figCSV = px.pie(localities9, values=localities9.Count, names=plotBy, color_discrete_sequence=px.colors.sequential.Turbo, height=pieHeigth1)  # colors: https://plotly.com/python/builtin-colorscales/
		figCSV.update_layout(legend=dict(font=dict(size = 17)))
		st.plotly_chart(figCSV, theme=None, use_container_width=True)  # Streamlit theme used without theme=None

elif tabs == 'Downloads':
	c1, c2, c3 = st.columns([1, 17, 1], gap='small')
	with c2:
		st.write('<b><font style="font-family: Linux Libertine Display, sans-serif; font-size: 2.1em">DOWNLOADS</font></b>', unsafe_allow_html=True)
		timestr = time.strftime('%Y-%m-%d_%H-%M-%S')
		st.write('<font style="font-size: 1.3em"><br></font>', unsafe_allow_html=True)

		col1, col2, col3, col4 = st.columns([11, 9, 11, 16], gap='small')
		with col1:
			st.write('<font style="font-size: 1.5em; color: #ffffab"><b>Current list of toponyms</b></font>', unsafe_allow_html=True)
		with col2:
			st.write('<font style="font-size: 1.5em">.csv file</font>', unsafe_allow_html=True)
		with col3:
			with open('resources/data/AssyrianProject-AllNoDupl.csv', 'rb') as file:
				st.download_button(
					label='Download',
					data=file,
					file_name=timestr + '_CNATv2-Toponyms.csv', use_container_width=True,
					)
		with col1:
			st.write('<font style="font-size: 1.5em; color: #ffffab"><b>Catalogue app</b></font>', unsafe_allow_html=True)
		with col2:
			st.write('<font style="font-size: 1.5em">available at GitHub</font>', unsafe_allow_html=True)
		with col3:
			st.link_button('Visit', 'https://github.com/KacaSas/Catalogue-of-Neo-Assyrian-Toponyms-v2', use_container_width=True)

# adding footer
footer = """<style>
background-color: transparent;
text-decoration: underline;
}

a:hover, a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0.1;
bottom: 0;
width: 99%;
background-color: transparent;
color: #575656;
text-align: left;
}
</style>
<div class="footer">
<p>KacaSas 2025</p>
</div>
"""
st.sidebar.markdown(footer, unsafe_allow_html=True)
