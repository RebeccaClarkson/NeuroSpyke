from inflection import humanize
import matplotlib.pyplot as plt


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


def create_axis_label(property_name):
    """
    Create axis label from property_name, either using property_label_dict
    or applying "humanize" from inflection module. 
    """

    last_char = property_name[-1] 

    if last_char.isdigit():
        # e.g. for property_name 'thresh4' look up 'thresh#' in dict
        property_name = property_name[:-1] + "#"

    label = property_label_dict.get(property_name, humanize(property_name))
    label = label.replace("#", last_char)

    return label

# rgb_colors dictionary for custom color names
rgb_colors = dict()
rgb_colors['dodgerblue'] = (.12, .56, 1)

# property_label_dict for use in creation of axis label names
property_label_dict = dict()
property_label_dict['doublet_index'] = 'doublet index (ISI2/ISI1)' 
property_label_dict['delta_thresh#'] = r'$\Delta$' + f"threshold (mV), AP# vs. AP1"
property_label_dict['reb_delta_t'] = f"rebound " + r'$\tau$'
