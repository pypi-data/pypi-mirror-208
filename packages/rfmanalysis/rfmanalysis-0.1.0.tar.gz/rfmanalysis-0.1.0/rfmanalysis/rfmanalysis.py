import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify

class RFMAnalysis:
    """
    Class for conducting RFM analysis on customer data.

    Attributes:
        data (DataFrame): Input customer data.
        id_col (str): Name of the column containing customer IDs.
        date_col (str): Name of the column containing transaction dates.
        revenue_col (str): Name of the column containing transaction revenues.
        rfm_data (DataFrame): RFM analysis results.

    Methods:
        __init__(self, data, id_col, date_col, revenue_col):
            Initializes the RFMAnalysis object.
        
        create_rfm_columns(self):
            Creates the RFM columns (Recency, Frequency, Monetary) from the input data.
        
        scale_rfm_columns(self):
            Scales the RFM columns into quartiles (R, F, M).
        
        rfm_scores(self):
            Calculates the RFM scores and segments for each customer.
        
        top_customers(self):
            Sorts the RFM data by segment to identify top customers.
        
        naming(row):
            Static method that assigns segment names based on RFM scores.
        
        give_names_to_segments(self):
            Assigns segment names to each customer based on RFM scores.
        
        segments_distribution(self):
            Computes the mean values and counts for each RFM segment.

       """
    def __init__(self, data, id_col, date_col, revenue_col):
        """
        Initializes the RFMAnalysis object.

        Args:
            data (DataFrame): Input customer data.
            id_col (str): Name of the column containing customer IDs.
            date_col (str): Name of the column containing transaction dates.
            revenue_col (str): Name of the column containing transaction revenues.

        """

        self.data = data
        self.id_col = id_col
        self.date_col = date_col
        self.revenue_col = revenue_col
        self.rfm_data = None

    def create_rfm_columns(self):
        """
        Creates the RFM columns (Recency, Frequency, Monetary) from the input data.

        """

        self.data[self.date_col] = pd.to_datetime(self.data[self.date_col])
        max_date = self.data[self.date_col].max()
        self.rfm_data = self.data.groupby(self.id_col).agg({
            self.date_col: lambda date: (max_date - date.max()).days,
            self.id_col: 'size',
            self.revenue_col: 'sum'
        })
        self.rfm_data.columns = ['Recency', 'Frequency', 'Monetary']
        self.rfm_data.reset_index(inplace=True)

    def scale_rfm_columns(self):
        """
        Scales the RFM columns into quartiles (R, F, M).

        """

        self.rfm_data['R'] = pd.qcut(self.rfm_data['Recency'], q=4, labels=['1', '2', '3', '4'])
        self.rfm_data['F'] = pd.qcut(self.rfm_data['Frequency'], q=4, labels=['4', '3', '2', '1'])
        self.rfm_data['M'] = pd.qcut(self.rfm_data['Monetary'], q=4, labels=['4', '3', '2', '1'])
    
    def rfm_scores(self):
        """
        Calculates the RFM scores and segments for each customer.

        """

        self.rfm_data['RFM_Score'] = self.rfm_data.R.astype(int) + self.rfm_data.F.astype(int) + self.rfm_data.M.astype(int)
        self.rfm_data['RFM_Segment'] = self.rfm_data.R.astype(str) + self.rfm_data.F.astype(str) + self.rfm_data.M.astype(str)
        self.rfm_data = self.rfm_data.sort_values('RFM_Segment', ascending=False)

    def top_customers(self):
        """
        Sorts the RFM data by segment to identify top customers.

        """

        self.rfm_data = self.rfm_data.sort_values('RFM_Segment', ascending=False)

    @staticmethod
    def naming(row):
        """
        Static method that assigns segment names based on RFM scores.

        Args:
            row (Series): A row of the RFM data.

        Returns:
            str: The segment name.

        """

        rfm_score = row['RFM_Score']

        if rfm_score >= 9:
            return "Can't Lose Them"
        elif 8 <= rfm_score < 9:
            return "Champions"
        elif 7 <= rfm_score < 8:
            return "Loyal/Committed"
        elif 6 <= rfm_score < 7:
            return "Potential"
        elif 5 <= rfm_score < 6:
            return "Promising"
        elif 4 <= rfm_score < 5:
            return "Requires Attention"
        else:
            return "Demands Activation"

    def give_names_to_segments(self):
        """
        Assigns segment names to each customer based on RFM scores.

        """

        self.rfm_data['Segment_Name'] = self.rfm_data.apply(self.naming, axis=1)

    def segments_distribution(self):
        """
        Computes the mean values and counts for each RFM segment.

        Returns:
            DataFrame: Mean values and counts for each RFM segment.

        """

        df = self.rfm_data.groupby('Segment_Name').agg({
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': ['mean', 'count']
        }).round(1)
        return df

                                                


class RFMVisualizer:
    """
    Class for visualizing RFM analysis results.

    Methods:
        plot_rfm(rfm_data):
            Plots the distribution of the RFM variables.

        visualize_segments(rfm_data):
            Visualizes the distribution of customers across RFM segments using a treemap.

        segment_distribution_barplot(rfm_data):
            Creates a bar plot showing the distribution of customers across RFM segments.

        segment_boxplot(rfm_data):
            Creates box plots for each RFM variable, grouped by segment.

        segment_comparison(rfm_data):
            Creates bar plots to compare the mean values of RFM variables across segments.

    """
    @staticmethod
    def plot_rfm(rfm_data):
        """
        Plots the distribution of the RFM variables.

        Args:
            rfm_data (DataFrame): RFM analysis results.

        """
        plt.figure(figsize=(12, 10))
        plt.subplot(3, 1, 1)
        sns.distplot(rfm_data['Recency'])
        plt.subplot(3, 1, 2)
        sns.distplot(rfm_data['Frequency'])
        plt.subplot(3, 1, 3)
        sns.distplot(rfm_data['Monetary'])
        plt.tight_layout()
        plt.show()

    @staticmethod
    def visualize_segments(rfm_data):
        """
        Visualizes the distribution of customers across RFM segments using a treemap.

        Args:
            rfm_data (DataFrame): RFM analysis results.

        """
        segment_names = ["Can't Lose Them", "Champions", "Loyal/Committed",
                         "Requires Attention", "Potential", "Promising",
                         "Demands Activation"]
        segment_counts = rfm_data['Segment_Name'].value_counts()
        segment_means = rfm_data.groupby('Segment_Name').agg({
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean'
        }).round(1)

        data = pd.concat([segment_means, segment_counts], axis=1)
        data.columns = ['RecencyMean', 'FrequencyMean', 'MonetaryMean', 'Count']

        fig = plt.gcf()
        ax = fig.add_subplot()
        squarify.plot(sizes=data['Count'], label=segment_names, color=sns.color_palette("Spectral", len(data)))

        plt.title("RFM Segments", fontsize=18, fontweight="bold")
        plt.axis('off')
        plt.show()



    @staticmethod
    def segment_distribution_barplot(rfm_data):
        """
        Creates a bar plot showing the distribution of customers across RFM segments.

        Args:
            rfm_data (DataFrame): RFM analysis results.

        """
        segment_counts = rfm_data['Segment_Name'].value_counts()
        segment_counts = segment_counts.sort_index()

        plt.figure(figsize=(8, 6))
        sns.barplot(x=segment_counts.index, y=segment_counts.values, color= "lightblue")
        plt.title("Segment Distribution", fontsize=18, fontweight="bold")
        plt.xlabel("Segments", fontsize=12)
        plt.ylabel("Count", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.show()

    @staticmethod
    def segment_boxplot(rfm_data):
        """
        Creates box plots for each RFM variable, grouped by segment.

        Args:
            rfm_data (DataFrame): RFM analysis results.

        """
        plt.figure(figsize=(15, 6))
        plt.subplot(1, 3, 1)
        sns.boxplot(x='Segment_Name', y='Recency', data=rfm_data, color='lightblue')
        plt.title("Recency by Segment", fontsize=18, fontweight="bold")
        plt.xlabel("Segment", fontsize=12)
        plt.ylabel("Recency", fontsize=12)
        plt.xticks(rotation=45, ha='right')

        plt.subplot(1, 3, 2)
        sns.boxplot(x='Segment_Name', y='Frequency', data=rfm_data, color='lightblue')
        plt.title("Frequency by Segment", fontsize=18, fontweight="bold")
        plt.xlabel("Segment", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        plt.xticks(rotation=45, ha='right')

        plt.subplot(1, 3, 3)
        sns.boxplot(x='Segment_Name', y='Monetary', data=rfm_data, color='lightblue')
        plt.title("Monetary by Segment", fontsize=18, fontweight="bold")
        plt.xlabel("Segment", fontsize=12)
        plt.ylabel("Monetary", fontsize=12)
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        plt.show()

        

    @staticmethod
    def segment_comparison(rfm_data):
        """
        Creates bar plots to compare the mean values of RFM variables across segments.

        Args:
            rfm_data (DataFrame): RFM analysis results.

        """
        metrics = ['Recency', 'Frequency', 'Monetary']
        fig, axes = plt.subplots(1, len(metrics), figsize=(15, 6))

        for i, metric in enumerate(metrics):
            segment_means = rfm_data.groupby('Segment_Name')[metric].mean().sort_values(ascending=False)
            ax = axes[i]
            sns.barplot(x=segment_means.index, y=segment_means.values, color="lightblue", ax=ax)
            ax.set_title(f"RFM {metric} Comparison")
            ax.set_xlabel("Segments")
            ax.set_ylabel(metric)
            ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.show()



