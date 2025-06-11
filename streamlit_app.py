import csv
import pandas as pd
import os
from os import listdir
from PIL import Image, ImageOps
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
import base64
import sys
import path

st.set_page_config(page_title='Cuneiform signs', page_icon='resources/icon/icon.png', layout='wide')  # change favicon and page title

def clearSignListForm():
	st.session_state['123998'] = ''

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

option = st.selectbox('Main menu', ('Cuneiform signs', 'Crop and resize images'), label_visibility='collapsed')

if option == 'Cuneiform signs':
	st.header('Cuneiform') 
	data = pd.read_csv('resources/SignList/SignList.csv')
	data = data.fillna(value='+++++++')

	st.write('<b><font style="font-size: 21px">Search sign</font></b> (case insensitive, regular expressions allowed):', unsafe_allow_html=True)

	colu1, colu2 = st.columns([19, 3])
	with colu1:
		searchSign = st.text_input('Search term (case insensitive, regular expressions allowed):', key=123998, label_visibility='collapsed')
	with colu2:
		clearSignListForm = st.button('Clear form', key='clearSignListForm', on_click=clearSignListForm, use_container_width=True)  # clear form

	FoundData0 = data.loc[data['Name'].str.contains(searchSign, case=False, regex=True)]
	FoundData1 = data.loc[data['Values'].str.contains(searchSign, case=False, regex=True)]
	FoundData2 = data.loc[data['Codepoint'].str.contains(searchSign, case=False, regex=True)]
	FoundData3 = data.loc[data['Sign'].str.contains(searchSign, case=False, regex=True)]
	FoundData4 = data.loc[data['Values3'].str.contains(searchSign, case=False, regex=True)]
	FoundData = pd.concat([FoundData0, FoundData1, FoundData2, FoundData3, FoundData4], axis=0, join='outer', ignore_index=False, keys=None)
	FoundData = FoundData.drop_duplicates(inplace=False)

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
				'    <span ref="eText" class="ag-header-cell-text" role="columnheader" style="font-size: 15px; text-align: right;"></span>' +
				'    <span ref="eFilter" class="ag-header-icon ag-filter-icon"></span>' +
				'  </div>' +
				'</div>'
		}
	)
	gb.configure_selection('', use_checkbox=True, groupSelectsChildren='Group checkbox select children')
	gb.configure_columns(['Name', 'Values', 'Meaning', 'MesZL', 'Values1', 'ABZ/Labat', 'Codepoint'], cellStyle=cellsytle_jscode)
	gb.configure_columns(['Sign'], cellStyle={'fontFamily': 'CuneiformComposite', 'color': 'white', 'backgroundColor': '#0E1117', 'font-size':'20px'})
	gb.configure_column('Values1', hide=True)
	gb.configure_column('Values2', hide=True)
	gb.configure_column('Values3', hide=True)
	gb.configure_column('Path', hide=True)
	gridOptions = gb.build()

	with st.expander('Show list of found items:', expanded=True):
		st.write('Found ', FoundData['Sign'].count(), 'items.')
		grid_response = AgGrid(
			FoundData,
			allow_unsafe_jscode=True,
			gridOptions=gridOptions,
			DataReturnMode='AS_INPUT',
			GridUpdateMode='MODEL_CHANGED',
			fit_columns_on_grid_load=True,
			theme='balham',  # themes: streamlit, light, dark/balham, blue, fresh, material
			enable_enterprise_modules=False,
			height=150, 
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
					st.write('<table border=0 width="100%"><tr><td width="40%" style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>End of 3<sup>rd</sup> millennia form:</b><br>– font <i>CuneiformComposite.ttf</i></td><td width="60%" style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "CuneiformComposite" style="font-size: 30pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Old Babylonian monumental form:</b><br>– font <i>SantakkuM.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "SantakkuM" style="font-size: 30pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Old Babylonian cursive form:</b><br>– font <i>Santakku.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "Santakku" style="font-size: 30pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Neo-Assyrian form:</b><br>– font <i>Assurbanipal.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "Assurbanipal" style="font-size: 35pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Neo-Assyrian form:</b><br>– font <i>Sinacherib.ttf</i></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><font face = "Sinacherib" style="font-size: 30pt" color = "#ffffab">', row['Sign'], '</font></td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Values:</b></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['Values1'], '</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>MesZL:</b></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['MesZL'], '</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>ABZ/Labat:</b></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['ABZ/Labat'], '</td></tr><tr><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm"><b>Unicode codepoint and name:</b></td><td style="border-top: 0pt; border-left: 0pt; border-right: 0pt; padding-top: 0.25cm; padding-bottom: 0.25cm; padding-left: 0.45cm">', row['Codepoint'], '</td></tr></table>', unsafe_allow_html=True)
				with c2:
					st.write('<b><font style="font-size: 23px">Image(s)</font></b>', unsafe_allow_html=True)
					path = './Signs' + '/' + str(row['Path'])

					colNumber = st.slider('Images size', 1, 13, 6, label_visibility='collapsed')
						
					try:
						files = listdir(path)
						images = pd.DataFrame({'file': files, 'Sign': files})
						images.set_index('file', inplace=True)

						foundSigns1 = []

						if len(images.columns) != 0:
							for index, row in images.iterrows():
								path1 = path + '/' + row['Sign']
								foundSigns1.append([path1, row['Sign']])

						foundSigns2 = pd.DataFrame(foundSigns1, columns = ['signPath', 'Image']).sort_values(by=['Image'])

						st.write('<b>Source directory: <font style="color:#ffffab">', path, '</font></b> (', len(foundSigns2), 'items found)', unsafe_allow_html=True)

						createGallery(foundSigns2)

					except:
						st.write('<font style="color:#FF4B4B; font-size: 16px"><b>No directory or images found!</b></font>', unsafe_allow_html=True)
						st.write(path)

					st.write('-------')

					colum1, colum2 = st.columns([1,39])
					with colum1:
						showAllSigns = st.checkbox('OK', label_visibility='collapsed')
					with colum2:
						st.write('<sub><b><font style="font-size: 19px">All images containing the string<font color = "#ffffab">', searchSign, '</font></b></sub>', unsafe_allow_html=True)
					if showAllSigns:
						path3 = './Signs/000-ALL'
						files3 = listdir(path3)
						images3 = pd.DataFrame({'file': files3, 'Sign3': files3})
						foundSigns = images3.loc[images3['Sign3'].str.contains(searchSign, case=False, regex=True)]

						foundSigns3 = []

						if len(foundSigns.columns) != 0:
							for index, row in foundSigns.iterrows():
								foundSigns3.append([path3 + '/' + row['Sign3'], row['Sign3']])

						foundSigns7 = pd.DataFrame(foundSigns3, columns = ['signPath', 'Image']).sort_values(by=['Image'])

						st.write('<b>Source directory: <font style="color:#ffffab">', path3, '</font></b> (', len(foundSigns7), 'items found)', unsafe_allow_html=True)

						createGallery(foundSigns7)

	with st.expander('Cuneify REPL by Jon Knowles:', expanded=False):
		
		st.markdown(f'<iframe src="https://amazing-chandrasekhar-e6c92b.netlify.app/index.html" width="100%" height="450" style="background-color: #c7c9c9"></iframe>', unsafe_allow_html=True)

	with st.expander('Notice and sources:', expanded=False):
		st.markdown('**Legend:**', unsafe_allow_html=True)
		st.markdown('<b>white</b> – values of MesZL<br><b><font color="#c5000b">dark-red</font></b> – values of Labat<br><b><font color="#579d1c">green</font></b> – values of ABZ<br><b><font color="#666666">gray</font></b> – commentaries', unsafe_allow_html=True)
		st.markdown('**Sources:**', unsafe_allow_html=True)
		st.markdown('– Borger, R. (2004): *Mesopotamisches Zeichenlexikon* [AOAT 305]. Münster: Ugarit-Verlag.<br>– Borger, R. (1981): *Assyrisch-babylonische Zeichenliste* [AOAT 1981]. Neukirchen-Vluyn.<br>– Labat, R. (1994): *Manuel d’épigraphie akkadienne*. Paris.<br>– Brünnow, Rudolf-Ernst (1889): *A classified list of all simple and compound Cuneiform ideographs occurring in the texts hitherto published, with their Assyro-Babylonian equivalents, phonetic values, etc.* Leyden: Brill.<br>– Tinney, S. et al. (2006): *The Pennsylvania Sumerian Dictionary Project* [PSD]. Philadelphia: University of Pennsylvania Museum of Anthropology and Archaeology. URL: http://psd.museum.upenn.edu/nepsd-frame.html.', unsafe_allow_html=True)
		st.markdown('**Fonts:**', unsafe_allow_html=True)
		st.markdown('– CuneiformComposite.ttf (S. Tinney): http://oracc.museum.upenn.edu/doc/help/visitingoracc/fonts/.<br>– SantakkuM.ttf (S. Vanséveren): https://www.hethport.uni-wuerzburg.de/cuneifont/.<br>– Santakku.ttf (S. Vanséveren): https://www.hethport.uni-wuerzburg.de/cuneifont/.<br>– Assurbanipal.ttf (S. Vanséveren): https://www.hethport.uni-wuerzburg.de/cuneifont/.<br>– Sinacherib.ttf: http://home.zcu.cz/~ksaskova/.', unsafe_allow_html=True)
		st.markdown('**Tools:**', unsafe_allow_html=True)
		st.markdown('– Cuneify REPL (Jon Knowles): https://amazing-chandrasekhar-e6c92b.netlify.app/index.html.<br>– CuneifyPlus (Tom Gillam): https://cuneify.herokuapp.com/.<br>– Cuneify (Steve Tinney): http://oracc.museum.upenn.edu/saao/knpp/cuneiformrevealed/cuneify/.<br>– KUR.NU.GI4.A – Cuneiform Script Analyzer (uyum): https://kurnugia.web.app/.<br>– GI-DUB – Sumerian Cuneiform Input Aid (uyum): https://qantuppi.web.app/.', unsafe_allow_html=True)

if option == 'Crop and resize images':
	st.header('Crop and resize images') 

	def text_field(label, columns=None, **input_params):
		column1, column2 = st.columns(columns or [1, 12])
		column1.markdown(label)
		input_params.setdefault('key', label)  # sets a default key to avoid duplicate key errors
		return column2.text_input('label', **input_params, label_visibility='collapsed')  # forward text input parameters

	order = text_field('Input directory:', value='./Signs/')  # input path
	order = text_field('Output files size:', value='128')  # size of the resulting canvas
	title = text_field('Output files suffix:', value='_new')  # new file suffix

	# ChatGPT - for RGB instead of grayscale, add .convert("RGB") instead of "L" and change the background color in Image.new("RGB", ...) to (255, 255, 255)

	if st.button('Crop and resize images', key='cropImages', use_container_width=True):
		if inputDir != '':
			padding = 3
			for filename in os.listdir(inputDir):
				if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
					filepath = os.path.join(inputDir, filename)
					img = Image.open(filepath).convert("L")  # conversion to grayscale
					inverted = ImageOps.invert(img)  # inversion to trim white edges
					bbox = inverted.getbbox()

					if bbox:
						cropped = img.crop(bbox)
						w, h = cropped.size

						# determine the square canvas size
						side = max(w, h) + 2 * padding
						square_img = Image.new("L", (side, side), 255)

						# calculate left and top offset for centering
						left = (side - w) // 2
						top = (side - h) // 2

						square_img.paste(cropped, (left, top))

						# resize to final size (e.g. 256x256)
						final_img = square_img.resize((outputSize, outputSize), Image.LANCZOS)

						# saving
						name, ext = os.path.splitext(filename)
						newName = f'{name}{suffix}{ext}'
						new_path = os.path.join(inputDir, newName)
						final_img.save(new_path)
						st.write('Saved as: ', newName)
			
