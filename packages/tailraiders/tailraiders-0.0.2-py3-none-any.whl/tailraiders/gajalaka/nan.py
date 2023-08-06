import pandas as pd

class Nan:
    """ Checks for NaN values and manipulate them """
    def __init__(self, df):
        self.df = df
        self.missing = df.isna().sum().to_frame()
        self.values = df.count().to_frame()
        self.rows = self.missing + self.values
        self.perc = round(self.missing / self.rows * 100, 2)
        self.dfnan = pd.concat([self.missing, self.values, self.rows, self.perc], axis = 1)
        self.dfnan.columns = ['total rows', 'rows with nan', 'rows without nan', 'perc nan']     

    def drop_cols(self, th = 20):
        """
        Drops columns based on a given threshold

        Parameters:
        ---------------
        self :
            The given name of the class

        th : int (default = 20)
            The percentage threshold of when columns should be dropped

        Returns:
        ----------------
        None :
            It makes it so that self.df is now edited to no longer have the dropped columns
        """

        self.nan_df = self.check[self.check['perc nan'] > th]
        dropcols = list(self.nan_df.index)
        print(f'The columns {dropcols} are being dropped')
        self.df = self.df.drop(dropcols, axis = 1)
        self.__init__(self.df)
    
    def fill_na(self, col, group, stat = 'mean'):
        """
        Fills dataframe columns based on a given group and method

        Parameters:
        --------------
        self :
            The given name of the class
        
        col : str
            The column name that will be filled
        
        group : str
            Column name that will be used to group
        
        stat : str (default = 'mean')
            The stat on how people will be grouped
            
        Returns:
        ----------------
        None :
            It makes it so that self.df is now edited to no longer have the dropped columns
        """

        self.df[col] = self.df[col].fillna(self.df.groupby(group)[col].transform(stat))
        self.__init__(self.df)
        
    def drop_na(self, axis = 0):
        """
        Drops columns based on the given axis

        Parameters:
        ---------------
        self :
            The given name of the class

        axis : int (default = 0)
            Bool value, either 0 or 1. 0 is for rows and 1 is for columns

        Returns:
        ----------------
        None :
            It makes it so that self.df is now edited to no longer have the dropped columns
        """

        self.df = self.df.dropna(axis = axis)
        self.__init__(self.df)