import csv
import pandas as pd
import os
from os import listdir
from PIL import Image, ImageOps
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
import base64

st.set_page_config(page_title='Cuneiform signs', page_icon='resources/icon/icon.png', layout='wide')  # change favicon and page title

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
fonts_css += load_font_css("Sinacherib", "resources/fonts/Sinacherib.ttf")
fonts_css += load_font_css("Assurbanipal", "resources/fonts/Assurbanipal.ttf")
fonts_css += load_font_css("Santakku", "resources/fonts/Santakku.ttf")
fonts_css += load_font_css("SantakkuM", "resources/fonts/SantakkuM.ttf")
fonts_css += load_font_css("OB Freie", "resources/fonts/OBFreie-Regular.ttf")
fonts_css += load_font_css("CuneiformComposite", "resources/fonts/CuneiformComposite.ttf")
fonts_css += load_font_css("Esagil", "resources/fonts/Esagil.ttf")

st.markdown(f"<style>{fonts_css}</style>", unsafe_allow_html=True)  # insert fonts into the app page

def clearSignListForm():
	st.session_state['searchSign'] = ''
	st.session_state['searchMesZL'] = ''
	st.session_state['searchABZ'] = ''
	st.session_state['searchCodepoint'] = ''

def createGallery(foundSignsList):
	# divide images into rows according to the number of columns
	for i in range(0, len(foundSignsList), colNumber):
		row = foundSignsList.iloc[i:i+colNumber]

		cols = st.columns(colNumber)  # create always exactly colNumber columns

		for j in range(colNumber):
			if j < len(row):
				row_foundSignsList = row.iloc[j]
				with cols[j]:
					st.image(Image.open(row_foundSignsList['signPath']), use_container_width=True)
					st.caption(f"<p style='text-align: center'>{row_foundSignsList['Image']}</p>", unsafe_allow_html=True)
			else:
				# empty column for proper alignment
				with cols[j]:
					st.empty()

# crop image names (remove suffix and part after '_', '-' or other chatacters)
def extractImageName(ImageName):
	noSuffix1 = ImageName.split('.')[0]
	noSuffix = noSuffix1.split('-')[0]
	return noSuffix.split('_')[0]

option = st.selectbox('Main menu', ('Cuneiform signs', 'Something else'), label_visibility='collapsed')

st.write('-------')

if option == 'Cuneiform signs':
	st.write('<b><font style="font-size: 36px">Search cuneiform signs</font></b> <br>(case insensitive, regular expressions allowed)', unsafe_allow_html=True)
	#st.header('Cuneiform') 
	
	colu1, colu2, colu3, colu4, colu5 = st.columns([1, 2, 1, 1, 1])
	with colu1:
		searchShape = st.selectbox('Initial wedge shape:', ('', '𒀸 AŠ', '𒋰 TAB', '𒀼 EŠ16', '𒀹 GE23', '𒌋 U', '𒁹 DIŠ'), key='searchShape', label_visibility='visible')
	with colu2:
		searchSign = st.text_input('Name/Value:', key='searchSign', label_visibility='visible')
	with colu3:
		searchMesZL = st.text_input('MesZL number:', key='searchMesZL', label_visibility='visible')
	with colu4:
		searchABZ = st.text_input('ABZ/Labat number:', key='searchABZ', label_visibility='visible')
	with colu5:
		searchCodepoint = st.text_input('Unicode codepoint:', key='searchCodepoint', label_visibility='visible')
	
	with colu5:
		clearSignListForm = st.button('Clear form', key='clearSignListForm', on_click=clearSignListForm, use_container_width=True)  # clear form

	data = pd.read_csv('resources/signList/SignList.csv', keep_default_na=False, na_values=[])

	if searchSign != '':
		foundSign1 = data.loc[data['Name'].str.contains(searchSign, case=False, regex=True)]
		foundSign2 = data.loc[data['Values'].str.contains(searchSign, case=False, regex=True)]
		foundSign3 = data.loc[data['Sign'].str.contains(searchSign, case=False, regex=True)]
		foundSign4 = data.loc[data['Values3'].str.contains(searchSign, case=False, regex=True)]
		foundSign = pd.concat([foundSign1, foundSign2, foundSign3, foundSign4], axis=0, join='outer', ignore_index=False, keys=None)
		foundSign = foundSign.drop_duplicates(inplace=False)
	else:
		foundSign = data

	if searchMesZL != '':
		foundMesZL = foundSign.loc[data['MesZL'].str.contains(searchMesZL, case=False, regex=True)]
	else:
		foundMesZL = foundSign

	if searchABZ != '':
		foundABZ = foundMesZL.loc[data['ABZ/Labat'].str.contains(searchABZ, case=False, regex=True)]
	else:
		foundABZ = foundMesZL

	if searchShape != '':
		#MesZL: 𒀸 – 1–208 (AŠ), 𒋰 – 209–504 (TAB), 𒀼 – 505–574 (EŠ16), 𒀹 – 575–660 (GE23), 𒌋 – 661–747 (U),  𒁹 – 748–907 (DIŠ)
		if searchShape == '𒀸 AŠ':
			foundShape = foundABZ[foundABZ['MesZL_nu'].between(1, 208)].sort_values(by=['MesZL'])
		elif searchShape == '𒋰 TAB':
			foundShape = foundABZ[foundABZ['MesZL_nu'].between(209, 504)].sort_values(by=['MesZL'])
		elif searchShape == '𒀼 EŠ16':
			foundShape = foundABZ[foundABZ['MesZL_nu'].between(505, 574)].sort_values(by=['MesZL'])
		elif searchShape == '𒀹 GE23':
			foundShape = foundABZ[foundABZ['MesZL_nu'].between(575, 660)].sort_values(by=['MesZL'])
		elif searchShape == '𒌋 U':
			foundShape = foundABZ[foundABZ['MesZL_nu'].between(661, 747)].sort_values(by=['MesZL'])
		elif searchShape == '𒁹 DIŠ':
			foundShape = foundABZ[foundABZ['MesZL_nu'].between(748, 907)].sort_values(by=['MesZL'])
		else:
			foundShape = foundABZ
	else:
		foundShape = foundABZ

	if searchCodepoint != '':
		searchCodepoint = searchCodepoint.replace('+', '\\+')
		searchCodepoint = searchCodepoint.replace('(', '\\(')
		searchCodepoint = searchCodepoint.replace(')', '\\)')
		searchCodepoint = searchCodepoint.replace('.', '\\.')
		foundCodepoint = foundShape.loc[data['Codepoint'].str.contains(searchCodepoint, case=False, regex=True)]
	else:
		foundCodepoint = foundShape

	foundData = foundCodepoint

	cellsytle_jscode = JsCode(
		"""
	function(params) {
		if (params.value != '–') {
			return {
				'color': 'white',
				'backgroundColor': '#0E1117',
				'font-size':'15px',
			}
		} else {
			return {
				'color': 'white',
				'backgroundColor': '#5B0808',
				'font-size':'15px',
			}
		}
	};


	"""
	)

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
				'    <span ref="eText" class="ag-header-cell-text" role="columnheader" style="font-size: 16px; text-align: right; color: gray;"></span>' +
				'    <span ref="eFilter" class="ag-header-icon ag-filter-icon"></span>' +
				'  </div>' +
				'</div>'
		}
	)
	gb.configure_selection('', use_checkbox=True, groupSelectsChildren='Group checkbox select children')
	gb.configure_columns(['Name', 'Values', 'Meaning', 'MesZL', 'Values1', 'ABZ/Labat', 'Codepoint'], cellStyle=cellsytle_jscode)
	gb.configure_column('Sign', cellStyle={'fontFamily': 'CuneiformComposite', 'color': 'white', 'backgroundColor': '#0E1117', 'font-size':'23px'})
	gb.configure_column('Sign1', hide=True)
	gb.configure_column('Values1', hide=True)
	gb.configure_column('Values2', hide=True)
	gb.configure_column('Values3', hide=True)
	gb.configure_column('Path', hide=True)
	gb.configure_column('MesZL_nu', hide=True)
	gb.configure_grid_options(rowHeight=37)  # set row height
	gridOptions = gb.build()

	with st.expander('List of found items:', expanded=True):
		st.write('Found ', foundData['Sign'].count(), 'items.')
		grid_response = AgGrid(
			foundData,
			allow_unsafe_jscode=True,
			gridOptions=gridOptions,
			DataReturnMode='AS_INPUT',
			GridUpdateMode='MODEL_CHANGED',
			fit_columns_on_grid_load=True,
			theme='streamlit',  # themes: streamlit, light, dark/balham, blue, fresh, material
			enable_enterprise_modules=False,
			height=190, 
			width='100%',
			reload_data=False
		)

		data = grid_response['data']
		selected = grid_response['selected_rows'] 
		df1 = pd.DataFrame(selected)

	with st.expander('Sign details:', expanded=True):
		if len(df1.columns) != 0:
			for index, row in df1.iterrows():
				st.header(row['Name'])
				c1, c2 = st.columns([7, 7], gap='small', border=True)
				with c1:
					st.write('<table border=0 width="100%"><tr><td width="40%" style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>End of the 3<sup>rd</sup> millennia form:</b><br>– font <i>CuneiformComposite.ttf</i></td><td width="60%" style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "CuneiformComposite" style="font-size: 30pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Old Babylonian monumental form:</b><br>– font <i>SantakkuM.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "SantakkuM" style="font-size: 32pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Old Babylonian literature form:</b><br>– font <i>OBFreie-Regular.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "OB Freie" style="font-size: 32pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Old Babylonian cursive form:</b><br>– font <i>Santakku.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "Santakku" style="font-size: 32pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Neo-Assyrian form:</b><br>– font <i>Assurbanipal.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "Assurbanipal" style="font-size: 35pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Neo-Assyrian form:</b><br>– font <i>Sinacherib.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "Sinacherib" style="font-size: 30pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Neo-Babylonian form:</b><br>– font <i>Esagil.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "Esagil" style="font-size: 32pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Values:</b></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['Values1'], '</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>MesZL:</b></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['MesZL'], '</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>ABZ/Labat:</b></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['ABZ/Labat'], '</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Unicode codepoint and name:</b></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['Codepoint'], '</td></tr></table>', unsafe_allow_html=True)
				with c2:
					st.write('<b><font style="font-size: 23px">Old Babylonian examples</font></b>', unsafe_allow_html=True)
					path = './resources/signs' + '/' + str(row['Path'])

					colNumber = st.slider('Column count:', 1, 13, 6, label_visibility='visible')
						
					try:
						files = listdir(path)
						images = pd.DataFrame({'file': files, 'Sign': files})
						images.set_index('file', inplace=True)

						images['noSuffix'] = images['Sign'].apply(extractImageName)

						foundSigns1 = []

						if len(images.columns) != 0:
							for index, row in images.iterrows():
								path1 = path + '/' + row['Sign']
								foundSigns1.append([path1, row['noSuffix']])

						foundSigns2 = pd.DataFrame(foundSigns1, columns = ['signPath', 'Image']).sort_values(by=['Image'])

						st.write('<b>Source directory: <font style="color:#ffffab">', path, '</font></b> (', len(foundSigns2), 'items found)', unsafe_allow_html=True)

						createGallery(foundSigns2)

					except:
						st.write('<font style="color:#FF4B4B; font-size: 16px"><b>No directory or images found!</b></font>', unsafe_allow_html=True)
						st.write(path)

					if searchSign != '':
						st.write('-------')

						colum1, colum2 = st.columns([1,39])
						with colum1:
							showAllSigns = st.checkbox('OK', label_visibility='collapsed')
						with colum2:
							st.write('<sub><b><font style="font-size: 19px">All images containing the string<font color = "#ffffab">', searchSign, '</font></b></sub>', unsafe_allow_html=True)
						if showAllSigns:
							path3 = './resources/signs/000-ALL'
							files3 = listdir(path3)
							images3 = pd.DataFrame({'file': files3, 'Sign3': files3})
							images3['noSuffix'] = images3['Sign3'].apply(extractImageName)
							foundSigns33 = images3.loc[images3['noSuffix'].str.contains(searchSign, case=False, regex=True)]

							foundSigns3 = []

							if len(foundSigns33.columns) != 0:
								for index, row in foundSigns33.iterrows():
									foundSigns3.append([path3 + '/' + row['Sign3'], row['noSuffix']])

							path9 = './resources/signs/000-ALL02'
							files9 = listdir(path9)
							images9 = pd.DataFrame({'file': files9, 'Sign9': files9})
							images9['noSuffix'] = images9['Sign9'].apply(extractImageName)
							foundSigns99 = images9.loc[images9['noSuffix'].str.contains(searchSign, case=False, regex=True)]

							foundSigns9 = []

							if len(foundSigns99.columns) != 0:
								for index, row in foundSigns99.iterrows():
									foundSigns9.append([path9 + '/' + row['Sign9'], row['noSuffix']])

							foundSigns77 = foundSigns3 + foundSigns9

							foundSigns7 = pd.DataFrame(foundSigns77, columns = ['signPath', 'Image']).sort_values(by=['Image'])

							st.write('<b>Source directory: <font style="color:#ffffab">', path3, '</font> and <font style="color:#ffffab">', path9, '</font></b> (', len(foundSigns7), 'items found)', unsafe_allow_html=True)

							createGallery(foundSigns7)
	st.write('-------')

	with st.expander('Cuneify REPL by Jon Knowles:', expanded=False):
		
		st.markdown(f'<iframe src="https://amazing-chandrasekhar-e6c92b.netlify.app/index.html" width="100%" height="450" style="background-color: #c7c9c9"></iframe>', unsafe_allow_html=True)

	with st.expander('Notice and sources:', expanded=False):
		st.markdown('**Legend:**', unsafe_allow_html=True)
		st.markdown('<b>white</b> – values of MesZL<br><b><font color="#c5000b">dark-red</font></b> – values of Labat<br><b><font color="#579d1c">green</font></b> – values of ABZ<br><b><font color="#666666">gray</font></b> – commentaries', unsafe_allow_html=True)
		st.markdown('**Sources:**', unsafe_allow_html=True)
		st.markdown('– Borger, R. (2004): *Mesopotamisches Zeichenlexikon* [AOAT 305]. Münster: Ugarit-Verlag.<br>– Borger, R. (1981): *Assyrisch-babylonische Zeichenliste* [AOAT 1981]. Neukirchen-Vluyn.<br>– Labat, R. (1994): *Manuel d’épigraphie akkadienne*. Paris.<br>– Brünnow, Rudolf-Ernst (1889): *A classified list of all simple and compound Cuneiform ideographs occurring in the texts hitherto published, with their Assyro-Babylonian equivalents, phonetic values, etc.* Leyden: Brill.<br>– Tinney, S. et al. (2006): *The Pennsylvania Sumerian Dictionary Project* [PSD]. Philadelphia: University of Pennsylvania Museum of Anthropology and Archaeology. URL: http://psd.museum.upenn.edu/nepsd-frame.html.', unsafe_allow_html=True)
		st.markdown('**Fonts:**', unsafe_allow_html=True)
		st.markdown('– CuneiformComposite.ttf (S. Tinney): http://oracc.museum.upenn.edu/doc/help/visitingoracc/fonts/.<br>– SantakkuM.ttf (S. Vanséveren): https://www.hethport.uni-wuerzburg.de/cuneifont/.<br>– Old Babylonian Freie (Corvin R. Ziegeler): https://refubium.fu-berlin.de/handle/fub188/45271 and https://github.com/crzfub/OB-Freie.<br>– Santakku.ttf (S. Vanséveren): https://www.hethport.uni-wuerzburg.de/cuneifont/.<br>– Assurbanipal.ttf (S. Vanséveren): https://www.hethport.uni-wuerzburg.de/cuneifont/.<br>– Sinacherib.ttf: http://home.zcu.cz/~ksaskova/.<br>– Esagil.ttf (S. Vanséveren): https://www.hethport.uni-wuerzburg.de/cuneifont/.', unsafe_allow_html=True)
		st.markdown('**Tools:**', unsafe_allow_html=True)
		st.markdown('– Cuneify REPL (Jon Knowles): https://amazing-chandrasekhar-e6c92b.netlify.app/index.html.<br>– CuneifyPlus (Tom Gillam): https://cuneify.herokuapp.com/.<br>– Cuneify (Steve Tinney): http://oracc.museum.upenn.edu/saao/knpp/cuneiformrevealed/cuneify/.<br>– KUR.NU.GI4.A – Cuneiform Script Analyzer (uyum): https://kurnugia.web.app/.<br>– GI-DUB – Sumerian Cuneiform Input Aid (uyum): https://qantuppi.web.app/.', unsafe_allow_html=True)

if option == 'Something else':
	st.write('Something else')
#	st.header('Something else') 

#	def text_field(label, columns=None, **input_params):
#		column1, column2 = st.columns(columns or [1, 12])
#		column1.markdown(label)
#		input_params.setdefault('key', label)  # sets a default key to avoid duplicate key errors
#		return column2.text_input('label', **input_params, label_visibility='collapsed')  # forward text input parameters

#	order = text_field('Input directory:', value='./Signs/')  # input path
#	order = text_field('Output files size:', value='128')  # size of the resulting canvas
#	title = text_field('Output files suffix:', value='_new')  # new file suffix

	# ChatGPT - for RGB instead of grayscale, add .convert("RGB") instead of "L" and change the background color in Image.new("RGB", ...) to (255, 255, 255)

#	if st.button('Crop and resize images', key='cropImages', use_container_width=True):
#		if inputDir != '':
#			padding = 3
#			for filename in os.listdir(inputDir):
#				if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
#					filepath = os.path.join(inputDir, filename)
#					img = Image.open(filepath).convert("L")  # conversion to grayscale
#					inverted = ImageOps.invert(img)  # inversion to trim white edges
#					bbox = inverted.getbbox()

#					if bbox:
#						cropped = img.crop(bbox)
#						w, h = cropped.size

						# determine the square canvas size
#						side = max(w, h) + 2 * padding
#						square_img = Image.new("L", (side, side), 255)

						# calculate left and top offset for centering
#						left = (side - w) // 2
#						top = (side - h) // 2

#						square_img.paste(cropped, (left, top))

						# resize to final size (e.g. 256x256)
#						final_img = square_img.resize((outputSize, outputSize), Image.LANCZOS)

						# saving
#						name, ext = os.path.splitext(filename)
#						newName = f'{name}{suffix}{ext}'
#						new_path = os.path.join(inputDir, newName)
#						final_img.save(new_path)
#						st.write('Saved as: ', newName)
			
