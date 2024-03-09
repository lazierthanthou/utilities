# Class DfStyler
class DfStyler():
	def __init__(self):
		return

	@staticmethod
	def get_styler_with_aggregate(df, style, agg_info={}):
		'''
		agg_info is a dictionary with index namw, column dict with col names as keys and value telling how to aggregate
		'''
		df_tot = DfStyler.get_aggregate_df(
			df,
			agg_info['columns'],
			index_name=agg_info['index_name']
		)

		styler = DfStyler.do_df_styling(df, style)

		tot_cols = [c for c in agg_info['columns']]
		style_tot = DfStyler.get_style_tot(style, tot_cols, agg_row_style=agg_info)

		styler_tot = DfStyler.do_df_styling(df_tot, style_tot)
		styler.concat(styler_tot)

		return styler

	@staticmethod
	def get_aggregate_df(df, cols_agg_info, index_name='Aggregate'):
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

	@staticmethod
	def get_total_df(df, sum_cols, tot_row_name='Total'):
		'''
		sum_cols is an array of columns for which sum to be done
		'''
		dict_rows = {c: (df[c].sum() if c in sum_cols else '') for c in df.columns}
		df_tot = pd.DataFrame(dict_rows, index=[tot_row_name])
		return df_tot

	@staticmethod
	def get_style_tot(style, tot_cols, agg_row_style={}):
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

	@staticmethod
	def do_df_styling(df, style):
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

	@staticmethod
	def display_side_by_side(*styler_tuple):
		html_str = ''
		for styler in styler_tuple:
			html_str += '<th style="text-align:center"><td style="vertical-align:top">'
			html_str += styler.to_html().replace('table', 'table style="display:inline"')
			html_str += '</td></th>'
		#IPython.display.display_html(html_str, raw=True)
		return html_str
