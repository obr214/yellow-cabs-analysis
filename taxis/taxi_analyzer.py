import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from DSGA1007 import settings
from functions import dictfetchall, format_date, get_centroid, get_distances
from collections import OrderedDict
from django.db import connection
from sklearn.cluster import DBSCAN
from matplotlib.backends.backend_pdf import PdfPages

"""
Class in charge of the analysis.

Has an instance variable named 'taxi_dataframe' of type Pandas Dataframe

Contains the Methods:
*** get_size()
*** get_dropoffs()
*** get_top_clusters()
*** get_pickup_distribution()
*** get_rate_stats()
*** get_distance_stats()
*** create_report()

"""


class TaxiAnalyzer:

    def __init__(self):
        self.taxi_dataframe = None

    def get_data(self, date, longitud, latitude):
        """
        Function that connects to the database and makes a query filtering by a pick up location and a date.
        Converts the queryset to a dataframe and save it into the instance variable.

        :param date: A specific date
        :param longitud: The pick up longitud coordinate
        :param latitude: The pick up latitude coordinate
        :return:
        """

        date_init, date_end = format_date(date)

        cursor = connection.cursor()

        cursor.execute('SELECT *, '
                       '(3959 * acos (cos ( radians(%s) )'
                       '* cos( radians( pickup_latitude ) )'
                       '* cos( radians( pickup_longitude ) '
                       '- radians( %s ) ) '
                       '+ sin ( radians( %s) )'
                       '* sin( radians( pickup_latitude ) )'
                       ')'
                       ') AS distance '
                       'FROM taxis_taxipickups '
                       'HAVING distance < 0.0621371 '
                       'AND pickup_datetime BETWEEN CAST(%s AS DATETIME) AND CAST(%s as DATETIME) '
                       'ORDER BY pickup_datetime',
                       [latitude, longitud, latitude, date_init, date_end]
                       )
        try:
            self.taxi_dataframe = pd.DataFrame(dictfetchall(cursor))
            self.taxi_dataframe['pickup_datetime'] = pd.to_datetime(self.taxi_dataframe['pickup_datetime'])
        except KeyError:
            raise KeyError("No data for this date or this location. Please select another one")

    def get_size(self):
        """
        Gets the number of rows of the instance variable dataframe

        :return: An integer number
        """
        return len(self.taxi_dataframe.index)

    def get_dropoffs(self):
        """
        Returns a list of the Drop Off coordinates of the instance variable dataframe
        :return: A list of latitudes and longitudes
        """
        dropoffs = self.taxi_dataframe[['dropoff_latitude', 'dropoff_longitude']]
        return dropoffs.values.tolist()

    def get_top_clusters(self, number_clusters):
        """
        Obtains the top n destinations.

        :param number_clusters: Number of top clusters
        :return: A list of centroids and the distance between the centroid and the farest point in that custer
        """
        try:
            #Creates a matrix with the drop offs
            coordinates = self.taxi_dataframe.as_matrix(columns=['dropoff_longitude', 'dropoff_latitude'])

            clusters = None
            number_of_rows = len(self.taxi_dataframe.index)
            cluster_stop_flag = True
            # Starting EPS
            current_eps = .005

            # Start clustering the points until the largest clusters contains around 15% of the total points
            while cluster_stop_flag:
                db_scan = DBSCAN(eps=current_eps, min_samples=1).fit(coordinates)
                labels = db_scan.labels_

                num_clusters = len(set(labels))

                clusters = pd.Series([coordinates[labels == i] for i in xrange(num_clusters)])
                sorted_len_clusters = sorted(clusters.values.tolist(), key=len, reverse=True)

                current_eps -= .0005
                if len(sorted_len_clusters[0]) <= int(number_of_rows*0.15):
                    cluster_stop_flag = False

                    top_ten_clusters = sorted_len_clusters[:number_clusters]

                    clusters = pd.Series(top_ten_clusters)

            # Obtains the distances between the centroid of each cluster and their coordinates.
            clusters_centroids = []
            for i, cluster in clusters.iteritems():

                list_center = get_centroid(cluster)

                distances = get_distances(cluster, list_center[0], list_center[1])

                # Obtains the largest distances to create a radius in the map.
                max_distance = np.amax(distances)
                list_center.append(max_distance)
                clusters_centroids.append(list_center)

            return clusters_centroids

        except LookupError:
            raise LookupError("Columns dropoff_longitude/dropoff_latitude not found")

    def get_pickup_distribution(self):
        """
        Obtains the number of pick ups per hour in a day.

        :return: An ordered dictionary where the keys are the hours and the values the number of pick ups
        """
        pickup_distribution = OrderedDict()
        #Creates the range of hours in a day
        hour_range = pd.date_range('00:00:00', periods=24, freq='H')

        #Creates the keys for all the hours. Format 'HH:MM'
        for hour in hour_range:
            hour_string = hour.strftime("%H:%M")
            pickup_distribution[hour_string] = 0

        times = pd.DatetimeIndex(self.taxi_dataframe.pickup_datetime)

        #Creates a group by given the hour.
        hour_groups = self.taxi_dataframe.groupby([times.hour]).size()
        for hg in hour_groups.index:
            hour_string = str(hg).zfill(2)+':00'
            pickup_distribution[hour_string] = int(hour_groups[hg])

        return pickup_distribution

    def get_rate_stats(self):
        """
        Obtains a summary statistics over the total_amount column

        :return: A dictionary with the the statistics
        """
        rate_summary = OrderedDict()

        rate_sum_statistics = self.taxi_dataframe['total_amount'].describe()
        rate_summary['Mean'] = rate_sum_statistics['mean']
        rate_summary['Std Dev'] = rate_sum_statistics['std']
        rate_summary['25%'] = rate_sum_statistics['25%']
        rate_summary['50%'] = rate_sum_statistics['50%']
        rate_summary['75%'] = rate_sum_statistics['75%']
        rate_summary['Max'] = rate_sum_statistics['max']

        return rate_summary

    def get_distance_stats(self):
        """
        Obtains a summary statistics over the trip_distance column

        :return: A dictionary with the the statistics
        """
        distance_summary = OrderedDict()

        distance_sum_statistics = self.taxi_dataframe['trip_distance'].describe()
        distance_summary['Mean'] = distance_sum_statistics['mean']
        distance_summary['Std Dev'] = distance_sum_statistics['std']
        distance_summary['25%'] = distance_sum_statistics['25%']
        distance_summary['50%'] = distance_sum_statistics['50%']
        distance_summary['75%'] = distance_sum_statistics['75%']
        distance_summary['Max'] = distance_sum_statistics['max']

        return distance_summary

    def get_amount_info(self):
        pass

    def create_report(self):
        url_file = settings.MEDIA_ROOT
        file_name = 'yellow_cap_analysis.pdf'
        print "Inside Create"
        print url_file

        with PdfPages(url_file+file_name) as pdf:

            #Get the pick up distribution
            pickup_dist = self.get_pickup_distribution()
            x = np.arange(len(pickup_dist))
            plt.bar(x, pickup_dist.values(), align="center")
            plt.xticks(x, pickup_dist.keys(), rotation='vertical')
            plt.title("Pick Ups Distribution Over Time")
            plt.xlabel("Time of the Day")
            plt.ylabel("Number of Pick Ups")
            pdf.savefig()
            plt.close()

            x = np.arange(0, 5, 0.1)
            y = np.sin(x)
            plt.plot(x, y)
            pdf.savefig()
            plt.close()


