from inflection import humanize
import matplotlib.pyplot as plt

def create_axis_label(property_keyword):
    """
    Create axis label from property_keyword, either using property_label_dict
    or applying "humanize" from inflection module. 
    """
    if property_keyword[-1].isdigit():
        number = property_keyword[-1]
        property_name = property_keyword[:-1] + "#"
        try:
            label_tmp = property_label_dict[property_name]
            label = label_tmp.replace("#", number)
        except:
            label = humanize(property_keyword)
    else:
        property_name = property_keyword
        try:
            label = property_label_dict[property_name]
        except:
            label = humanize(property_name)
    return label

def D1_D3_scatter_plot(df, output_dir,  x_property, y_property):
    """ 
    Scatter plot of y_property vs. x_property with cells grouped by whether
    genetic marker is D1 or D3
    """
    D1_cells = df[df['genetic_marker'] == 'D1']
    D3_cells = df[df['genetic_marker'] == 'D3']
    
    plt.figure()
    plt.scatter(D1_cells[x_property], D1_cells[y_property], 
            marker = 'o', color = 'k', label='D1')
    plt.scatter(D3_cells[x_property], D3_cells[y_property],
            marker = 'o', color = rgb_colors['dodgerblue'] , label='D3')

    xlabel = create_axis_label(x_property)
    ylabel = create_axis_label(y_property)

    plt.xlabel(xlabel); plt.ylabel(ylabel)
    plt.legend()
    
    file_name = f"D1_D3_scatter_{y_property}_vs_{x_property}.png"
    plt.savefig(output_dir + file_name)



rgb_colors = dict()
rgb_colors['dodgerblue'] = (.12, .56, 1)


property_label_dict = dict()
property_label_dict['doublet_index'] = 'doublet index (ISI2/ISI1)' 
property_label_dict['delta_thresh#'] = r'$\Delta$' + f"threshold (mV), AP# vs. AP1"
property_label_dict['reb_delta_t'] = f"rebound " + r'$\tau$'

