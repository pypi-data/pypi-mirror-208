import seaborn as sns
import matplotlib.pyplot as plt

class Plot:
    """ Code for making catplots """
    def __init__(self, df, xlim_low = None, xlim_high = None):
        self.data = df
        self.xlim_low = xlim_low
        self.xlim_high = xlim_high
        sns.set_style('darkgrid')

    def cat(self, x, y, hue = None, kind = 'bar'):
        """
        A function to make a catplot, based on the dataframe used for Gajalaka

        Parameters:
        --------------
        self :
            The given name of the class

        x : str
            Column name for x parameter
        
        y : str
            Column name for y parameter

        hue : str (default = None)
            A column name for differentiating per category

        kind : str (default = 'bar')
            The kind of plot you want to make, options are:
                strip, swarm, box, violin, boxen, point, bar and count

        Returns:
        --------------
        None :
            Instead it shows the plot for which the parameters are given
        """

        sns.catplot(data = self.data, x = x, y = y, hue = hue, kind = kind)
        plt.xlim(self.xlim_low, self.xlim_high)
        plt.title(label = f'{kind}plot with x: {x} and y: {y}')
        plt.show()
     
    def rel(self, x, y, hue = None, kind = 'scatter'):
        """
        A function to make a relplot, based on the dataframe used for Gajalaka

        Parameters:
        --------------
        self :
            The given name of the class

        x : str
            Column name for x parameter
        
        y : str
            Column name for y parameter

        hue : str (default = None)
            A column name for differentiating per category

        kind : str (default = 'bar')
            The kind of plot you want to make, options are:
                strip, swarm, box, violin, boxen, point, bar and count

        Returns:
        --------------
        None :
            Instead it shows the plot for which the parameters are given
        """
        
        sns.relplot(data = self.data, x = x, y = y, hue = hue, kind = kind)
        plt.xlim(self.xlim_low, self.xlim_high)
        plt.title(label = f'{kind}plot with x: {x} and y: {y}')
        plt.show()