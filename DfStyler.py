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

	ROW_STYLE_BLUE = "background-color:#cfe2f3"
	ROW_STYLE_ORANGE = "background-color:#fce5cd"
	ROW_STYLE_GREEN = "background-color:#d9ead3"
	ROW_STYLE_YELLOW = "background-color:#fff2cc"
	ROW_STYLE_GOLD = "background-color:#ffe9b8"

	TABLE_CAPTION_STYLE = {
		'selector': 'caption',
		'props': [
			('color', 'black'),
			('background-color', '#c9daf8'), #'hsl(189, 8%, 91%)'),
			('font-weight', 'bold'),
			('font-size', '17px')
		]
	}

	def __init__(self):
		self.DEFAULT_TABLE_STYLE = [
			self.TABLE_CAPTION_STYLE,
			self.TABLE_COL_HEADING_STYLE,
			self.TABLE_ROW_HEADING_STYLE,
			self.TABLE_DATA_CENTRED,
		]
		return

	def get_styler_with_aggregate(self, df, style, agg_info={}):
		'''
		agg_info is a dictionary with index namw, column dict with col names as keys and value telling how to aggregate
		'''
		if 'index_name' not in agg_info:
			agg_info['index_name'] = 'Aggregate'
		if 'row_props' not in agg_info:
			agg_info['row_props'] = self.ROW_STYLE_AGGREGATE

		df_tot = self.get_aggregate_df(
			df,
			agg_info['columns'],
			index_name=agg_info['index_name']
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

	def get_total_df(self, df, sum_cols, tot_row_name='Total'):
		'''
		sum_cols is an array of columns for which sum to be done
		'''
		dict_rows = {c: (df[c].sum() if c in sum_cols else '') for c in df.columns}
		df_tot = pd.DataFrame(dict_rows, index=[tot_row_name])
		return df_tot

	def get_style_tot(self, style, tot_cols, agg_row_style={}):
		style_tot = {}
		imitate = ['show_cols', 'hide_cols', 'hide_rows',
				   'hide_col_index', 'hide_row_index',
				   'table_style', 'table_attributes', 'row_styles']
		for key in [k for k in imitate if k in style]:
			style_tot[key] = style[key]

		if 'col_formats' in style:
			style_tot['col_formats'] = {k: v for k, v in style['col_formats'].items() if k in tot_cols}

		if 'properties' in style:
			style_tot['properties'] = []
			if 'row_props' in agg_row_style:
				style_tot['properties'].append({
					'subset_rows': [agg_row_style['index_name']],
					'properties': agg_row_style['row_props']
				})

			for p in style['properties']:
				if ('subset_cols' in p) or ('subset_rows' in p):
					style_tot['properties'].append(p)

		return style_tot

	def get_col_style_properties(self, col_info={}):
		obj = []
		if 'all' in col_info:
			props = {'text-align': 'center',}
			cols = col_info['all']
			obj.append({'subset_cols': cols, 'properties': props})

		if 'row_identifier' in col_info:
			props = {'text-align': 'left', 'font-weight': 'bold',}
			cols = [col_info['row_identifier']]
			obj.append({'subset_cols': cols, 'properties': props})

		if 'golden' in col_info:
			props = {'font-weight': 'bold', 'font-size': '1.1em', 'background-color': OUR_GOLD}
			cols = [col_info['golden']]
			obj.append({'subset_cols': cols, 'properties': props})

		return obj

	def do_df_styling(self, df, style):
		styler = df.style

		if 'col_formats' in style:
			given = style['col_formats']
			formatter = {col: given[col] for col in given if col in df.columns}
			styler.format(style['col_formats'], na_rep='')

		if 'slice_formats' in style:
			for info in style['slice_formats']:
				slice_, format_ = info[0], info[1]
				styler.format(format_, subset=slice_)

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

		if 'table_style' in style:
			styler.set_table_styles(style['table_style'])

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
