## wes-palette

[![PyPI](https://img.shields.io/pypi/v/wes-palette)](https://pypi.org/project/wes-palette/)
[![license](https://img.shields.io/github/license/au2232/wes-palette)](https://github.com/au2232/wes-palette/LICENSE)
[![issues](https://img.shields.io/github/issues/au2232/wes-palette)](https://github.com/au2232/wes-palette/issues)
[![build](https://img.shields.io/github/actions/workflow/status/au2232/wes_palette/build.yml)](https://github.com/au2232/wes_palette/actions/workflows/build.yml)
[![docs](https://img.shields.io/github/actions/workflow/status/au2232/wes-palette/docs.yml?label=docs)](https://ew2664.github.io/wes-palette/)
[![coverage](https://img.shields.io/codecov/c/github/au2232/wes_palette?token=5542beb1-1af8-4185-8340-fda0d36d528a)](https://coveralls.io/github/au2232/wes-palette)



wes-palette is a Wes Anderson film color palettes for matplotlib based on [vapeplot](https://github.com/dantaki/vapeplot)

## Installation

    pip install wes-palette

## Examples

![wes anderson palettes](palettes.png)

## Basic Usage

Import the package
  
    import wes_palette as wes
    
Generate a custom diverging colormap

    cmap = wes.cmap('budapest')
    
Create your graph with matplotlib and then display the plot:
    
    plt.show()

## Example

    # Create a visualization
    sns.set_theme(style="white")

    # Generate a large random dataset
    rs = np.random.RandomState(33)
    d = pd.DataFrame(data=rs.normal(size=(100, 26)),
                 columns=list(ascii_letters[26:]))

    # Compute the correlation matrix
    corr = d.corr()

    # Generate a mask for the upper tria#ngle
    mask = np.triu(np.ones_like(corr, dtype=bool))

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = wes.cmap('dispatch')

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})

    plt.show()
    
![example](examplegraph1.png)
![example](examplegraph2.png)
![example](examplegraph3.png)

## Contributing

See CONTRIBUTING.md

## License

Protected under MIT Liscense.
