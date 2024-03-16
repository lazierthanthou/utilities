import pandas as pd

OUR_BLUE = '#cfe2f3'
OUR_GOLD = '#ffe9b8'
OUR_GREEN = '#d9ead3'
OUR_ORANGE = '#fce5cd'
OUR_YELLOW = '#fff2cc'

# Class DfStyler
class DfStyler():
	TABLE_STYLE = {
		'selector': 'td',
		'props': [
			('text-align', 'center'),
			('border', '1px dotted black'),
		]
	}

	TABLE_COL_HEADING_STYLE = {
		'selector': 'th.col_heading',
		'props': [
			('text-align', 'center'),
		]
	}

	TABLE_ROW_HEADING_STYLE = {
		'selector': 'th.row_heading',
		'props': [
			('text-align', 'left'),
		]
	}

	TABLE_DATA_CENTRED = {
		'selector': 'td.data',
		'props': [
			('text-align', 'center'),
		]
	}

	ROW_STYLE_AGGREGATE = {
		'text-align': 'center',
		'font-size': '15px',
		'font-weight': 'bold',
		'background-color': OUR_GREEN,
	}

	STYLE_EMPHASIS = {
		'font-weight': 'bold',
	}

	TABLE_CAPTION_STYLE = {
		'selector': 'caption',
		'props': [
			('color', 'black'),
			('background-color', '#c9daf8'), #'hsl(189, 8%, 91%)'),
			('font-weight', 'bold'),
			('font-size', '17px')
		]
	}

	# COMMON STYLES
	S_LEFT_BOLD = {'text-align': 'left', 'font-weight': 'bold'}
	S_LEFT = {'text-align': 'left'}
	S_RIGHT = {'text-align': 'right'}
	S_CENTER = {'text-align': 'center'}
	S_GOLDEN = {'text-align': 'center', 'font-weight': 'bold', 'background-color': OUR_GOLD}

	def __init__(self):
		self.DEFAULT_TABLE_STYLE = [
			self.TABLE_CAPTION_STYLE,
			self.TABLE_COL_HEADING_STYLE,
			self.TABLE_ROW_HEADING_STYLE,
		]
		return

	def _get_display_info(self, columns_info):
		agg_info = { 'columns': {} }

		rename_info, col_formats = {}, {}
		for k, v in columns_info.items():
			if 'format' in v:
				if 'name' in v:
					col_formats[v['name']] = v['format']
				else:
					col_formats[k] = v['format']

			if 'aggregate' in v:
				if k == '__index__':
					agg_info['index_name'] = v['aggregate']
				else:
					if 'name' in v:
						agg_info['columns'][v['name']] = v['aggregate']
					else:
						agg_info['columns'][k] = v['aggregate']

			if 'name' in v:
				if k != '__index__':
					rename_info[k] = v['name']

		show_cols = [k for k in columns_info if k != '__index__']
		return show_cols, rename_info, col_formats, agg_info

	def get_styler_with_aggregate_v3(self, df, style, columns_info={}):
		'''
		columns_info is a dictionary in which:
			keys are column names, and
			values are dictionaries with 'name', 'format' and 'aggregate' as keys
		'''

		show_cols, rename_info, col_formats, agg_info = self._get_display_info(columns_info)
		style['col_formats'] = col_formats

		obj = []
		# some styling of columns info produced here
		for col, info in columns_info.items():
			if 'name' in info:
				col_name = info['name']
			else:
				col_name = col

			if 'style' in info:
				obj.append({'subset_cols': [col_name], 'properties': info['style']})
			else:
				obj.append({'subset_cols': [col_name], 'properties': self.S_CENTER})
		style['properties'] = obj

		df = df[show_cols]
		df = df.rename(columns=rename_info)

		if 'index_name' not in agg_info:
			agg_info['index_name'] = 'Aggregate'
		if 'row_props' not in agg_info:
			agg_info['row_props'] = self.ROW_STYLE_AGGREGATE

		df_tot = self.get_aggregate_df(
			df, agg_info['columns'], index_name=agg_info['index_name']
		)

		styler = self.do_df_styling(df, style)

		tot_cols = [c for c in agg_info['columns']]
		style_tot = self.get_style_tot(style, tot_cols, agg_row_style=agg_info)

		styler_tot = self.do_df_styling(df_tot, style_tot)
		styler.concat(styler_tot)

		return styler

	def get_styler_with_aggregate(self, df, style, agg_info={}):
		'''
		agg_info is a dictionary with index name, column dict with col names as keys and value telling how to aggregate
		'''
		if 'index_name' not in agg_info:
			agg_info['index_name'] = 'Aggregate'
		if 'row_props' not in agg_info:
			agg_info['row_props'] = self.ROW_STYLE_AGGREGATE

		df_tot = self.get_aggregate_df(
			df, agg_info['columns'], index_name=agg_info['index_name']
		)

		styler = self.do_df_styling(df, style)

		tot_cols = [c for c in agg_info['columns']]
		style_tot = self.get_style_tot(style, tot_cols, agg_row_style=agg_info)

		styler_tot = self.do_df_styling(df_tot, style_tot)
		styler.concat(styler_tot)

		return styler

	def get_aggregate_df(self, df, cols_agg_info, index_name='Aggregate'):
		'''
		cols_agg_info is a dictionary with column names as keys and value telling how to aggregate
		'''
		dict_rows = {c: '' for c in df.columns}
		valid_cols = [c for c in cols_agg_info if c in df.columns]
		for c in valid_cols:
			if cols_agg_info[c] == 'sum':
				dict_rows[c] = df[c].sum()
			else: # string to be used as it is in these columns
				dict_rows[c] = cols_agg_info[c]

		df_tot = pd.DataFrame(dict_rows, index=[index_name])
		return df_tot

	def _preprocess_row_styles(self, row_styles):
		'''
		row_styles is a list of dictionaries.
		Each dictionary has the key 'indices' and 'style'.
		The 'style' value is again a dictionary containing CSS attr as keys and values.
		'''
		properties = []
		row_head_styles = {}
		for item in row_styles:
			properties.append({
				'subset_rows': item['indices'],
				'properties': item['style'],
			})
			s = [f'{k}:{v}' for k, v in item['style'].items()]
			s = '; '.join(s)
			for idx in item['indices']:
				row_head_styles[idx] = s
		return properties, row_head_styles

	def get_style_tot(self, style, tot_cols, agg_row_style={}):
		style_tot = {}
		imitate = ['show_cols', 'hide_cols', 'hide_rows',
				   'hide_col_index', 'hide_row_index',
				   'table_style', 'table_attributes', 'row_styles']
		for key in [k for k in imitate if k in style]:
			style_tot[key] = style[key]

		if 'col_formats' in style:
			style_tot['col_formats'] = {k: v for k, v in style['col_formats'].items() if k in tot_cols}

		style_tot['properties'] = []
		if 'row_props' in agg_row_style:
			style_tot['properties'].append({
				'subset_rows': [agg_row_style['index_name']],
				'properties': agg_row_style['row_props']
			})
			# now, for the index cell itself
			style_tot['row_head_styles'] = {}
			# apply style to the index cell too
			s = [f'{k}:{v}' for k, v in agg_row_style['row_props'].items()]
			s = '; '.join(s)
			style_tot['row_head_styles'][agg_row_style['index_name']] = s

		if 'properties' in style:
			for p in style['properties']:
				if ('subset_cols' in p) or ('subset_rows' in p):
					style_tot['properties'].append(p)

		return style_tot

	def do_df_styling(self, df, style):
		# Preprocess style['row_styles']: required for styling index cells
		if 'row_styles' in style:
			properties, row_head_styles = self._preprocess_row_styles(style['row_styles'])

			if 'row_head_styles' not in style:
				style['row_head_styles'] = {}
			style['row_head_styles'].update(row_head_styles)

			if 'properties' not in style:
				style['properties'] = []
			style['properties'] += properties

		# Now use the info in style variable to do actual styling
		styler = df.style

		if 'col_formats' in style:
			given = style['col_formats']
			formatter = {col: given[col] for col in given if col in df.columns}
			styler.format(style['col_formats'], na_rep='')

		if 'slice_formats' in style:
			for info in style['slice_formats']:
				slice_, format_ = info[0], info[1]
				styler.format(format_, subset=slice_)

		if 'row_head_styles' in style:
			d = style['row_head_styles']
			styler.map_index(lambda idx: d[idx] if idx in d else '', axis=0)

		if 'properties' in style:
			for p in style['properties']:
				if 'subset' in p:
					styler.set_properties(**p['properties'], subset=p['subset'])
				if 'subset_cols' in p:
					valid_cols = [i for i in p['subset_cols'] if i in df.columns]
					slice_ = (df.index, valid_cols)
					styler.set_properties(**p['properties'], subset=slice_)
				if 'subset_rows' in p:
					valid_idx = [i for i in p['subset_rows'] if i in df.index]
					slice_ = (valid_idx, df.columns)
					styler.set_properties(**p['properties'], subset=slice_)

		if 'caption' in style:
			styler.set_caption(style['caption'])
			if 'caption_style' in style:
				styler.set_table_styles([style['caption_style']], overwrite=False)
			else:
				styler.set_table_styles([self.TABLE_CAPTION_STYLE], overwrite=False)

		if 'table_style' in style:
			styler.set_table_styles(style['table_style'], overwrite=False)

		if 'table_attributes' in style:
			styler.set_table_attributes(style['table_attributes'])

		if 'show_cols' in style:
			show_cols = style['show_cols']
			styler.hide([c for c in df.columns if c not in show_cols], axis='columns')

		if 'hide_cols' in style:
			hide_cols = style['hide_cols']
			styler.hide([c for c in df.columns if c in hide_cols], axis='columns')

		if 'hide_rows' in style:
			hide_rows = style['hide_rows']
			styler.hide([c for c in df.index if c in hide_rows], axis='index')

		if 'hide_col_index' in style:
			styler.hide(axis='columns')

		if 'hide_row_index' in style:
			styler.hide(axis='index')

		return styler

	def display_side_by_side(self, *styler_tuple):
		html_str = ''
		for styler in styler_tuple:
			html_str += '<th style="text-align:center"><td style="vertical-align:top">'
			html_str += styler.to_html().replace('table', 'table style="display:inline"')
			html_str += '</td></th>'
		#IPython.display.display_html(html_str, raw=True)
		return html_str
