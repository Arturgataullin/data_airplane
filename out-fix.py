import polars as pl

'''
Приведение файлов к заданному общему виду 
'''

def parse_csv():
    df_csv = pl.read_csv('BoardingData.csv', separator=';')
    print(df_csv.head())

    df_csv_trans = df_csv.select([
        pl.col('PassengerFirstName').alias('FirstName'),
        pl.col('PassengerLastName').alias('LastName'),
        pl.col("FlightDate").str.replace(r"(\d{4})-(\d{2})-(\d{2})", r"$3.$2.$1").alias("DepartDate"),
        pl.col('FlightTime').alias('DepartTime'),
        pl.lit('N/A').alias('ArrivalDate'),
        pl.lit('N/A').alias('ArrivalTime'),
        pl.col('FlightNumber'),
        pl.lit('N/A').alias('From'),
        pl.lit('N/A').alias('Dest'),
        pl.when(pl.col('BookingCode') == 'Not presented').then(pl.lit('N/A')).otherwise(pl.col('BookingCode')).alias('Fare'),
        pl.lit('N/A').alias('CountryTo'),
        pl.lit('N/A').alias('CountryFrom'),
        pl.col('Destination').str.to_uppercase().alias('CityTo'),
        pl.lit('N/A').alias('CityFrom'),
        pl.when(pl.col('TicketNumber') == 'Not presented').then(pl.lit('N/A')).otherwise(pl.col('TicketNumber')).alias('ETicketNumber'),
        pl.lit('N/A').alias('TravelClass'),
        pl.lit('N/A').alias('CardNumber'),
        pl.col('PassengerDocument'),
        pl.col('PassengerSex').alias('Sex'),
        pl.col('PassengerSecondName').alias('SecondName'),
        pl.col("PassengerBirthDate").str.replace(r"(\d{2})/(\d{2})/(\d{4})", r"$2.$1.$3").alias("BirthDate"),
        pl.when(pl.col('CodeShare') == 'Own').then(pl.lit('NO')).otherwise(pl.lit('YES')).alias('CodeShare')

    ])
    df_csv_trans.write_csv("correct_csv.csv", separator=';')
    print(df_csv_trans.head())

def parse_tab():
    df_tab = pl.read_csv('tab.csv', separator=';')
    print(df_tab.head())
    print(df_tab.columns)

    df_tab_trans = df_tab.select([
        pl.col('FirstName').str.replace("'", "").str.replace("J", "Y").str.replace("J", "Y").str.replace("J", "Y"),
        pl.col('LastName').str.replace("'", "").str.replace("J", "Y").str.replace("J", "Y").str.replace("J", "Y"),
        pl.col("DepartDate"),
        pl.col('DepartTime'),
        pl.col('ArrivalDate'),
        pl.col('ArrivalTime'),
        pl.col('FlightNumber'),
        pl.col('From'),
        pl.col('Dest'),
        pl.col('Fare').alias('Fare'),
        pl.lit('N/A').alias('CountryTo'),
        pl.lit('N/A').alias('CountryFrom'),
        pl.lit('N/A').alias('CityTo'),
        pl.lit('N/A').alias('CityFrom'),
        pl.col('e-Ticket').alias('ETicketNumber'),
        pl.col('TravelClass'),
        pl.when(pl.col('AdditionalInfo2') != 'N/A')
        .then(pl.col('AdditionalInfo2').str.slice(3, pl.col('AdditionalInfo2').str.len_chars()))
        .otherwise(pl.col('AdditionalInfo2'))
        .alias('CardNumber'),
        pl.col('TravelDoc').alias('PassengerDocument'),
        pl.col('SecondName').str.replace("'", "").str.replace("J", "Y").str.replace("J", "Y").str.replace("J", "Y"),
        pl.col('BirthDate').alias("BirthDate"),
        pl.col('AgentInfo'),
        pl.col('CodeSh').alias('CodeShare'),
        pl.col('Fare_duplicated_0').alias('FareBasisCode')
    ])
    with pl.Config(tbl_cols=-1):
        print(df_tab_trans.head(n=10))

    df_tab_trans.write_csv("correct_tab.csv", separator=';')


def main():
    parse_csv()
    parse_tab()


if __name__ == "__main__":
    main()