from inflection import humanize
import matplotlib.pyplot as plt

def D1_D3_scatter_subplots(df, xy_pairs, output_path):
    number_of_subplots = len(xy_pairs)
    columns = 2
    rows = number_of_subplots%columns + number_of_subplots//columns
    position = range(1, number_of_subplots + 1) 
    fig = plt.figure(figsize=(rows*5, columns*5))
    
    i = 0
    for pair in xy_pairs:
        fig.add_subplot(rows, columns, position[i])
        D1_D3_scatter_plot(df, pair[0], pair[1], new_figure=0)
        if i == 1:
            plt.legend()
        i += 1
    plt.suptitle('D1R- vs D3R-expressing pyramidal neuron electrophysiology')
    plt.savefig(output_path)


def D1_D3_scatter_plot(df, x_property, y_property, output_dir=None, new_figure=1):
    """ 
    Scatter plot of y_property vs. x_property with cells grouped by whether
    genetic marker is D1 or D3
    """
    D1_cells = df[df['genetic_marker'] == 'D1']
    D3_cells = df[df['genetic_marker'] == 'D3']

    if new_figure:  
        plt.figure()

    plt.scatter(D1_cells[x_property], D1_cells[y_property], 
            marker = 'o', color = 'k', label='D1')
    plt.scatter(D3_cells[x_property], D3_cells[y_property],
            marker = 'o', color = rgb_colors['dodgerblue'] , label='D3')
    
    x_min = min(min(D1_cells[x_property]), min(D3_cells[x_property]))
    y_min = min(min(D1_cells[y_property]), min(D3_cells[y_property]))
    
    if x_min > 0:
        plt.xlim(xmin=0)
    if y_min > 0:
        plt.ylim(ymin=0)
    
    xlabel = create_axis_label(x_property)
    ylabel = create_axis_label(y_property)

    plt.xlabel(xlabel); plt.ylabel(ylabel)

    if new_figure:
        plt.legend()

    file_name = f"D1_D3_scatter_{y_property}_vs_{x_property}.png"
    if output_dir:
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
property_label_dict = {
        'dVdt_at_percent_APamp__20__rising#' : f"dVdt (AP#) @ 20% AP amp.",
        'delta_thresh#': r'$\Delta$' + f"threshold (mV), AP# vs. AP1",
        'doublet_index': 'doublet index (ISI2/ISI1)',
        'reb_delta_t' : f"rebound " + r'$\tau$' + ' (ms)',
        'sag_fit_amplitude' : f"sag amplitude (mv)"
        }
