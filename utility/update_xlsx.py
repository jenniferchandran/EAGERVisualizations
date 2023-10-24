from util import *

relative_file_path = "../raw_trail_journal_data/additional_csv/"

df = load_raw_data_to_df("../raw_trail_journal_data/xlsx")

print(df)

print(f"columns: {df.columns}")

new_df = pd.DataFrame()

years = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
for year in years:
    file = f"tj{year}-v3.csv"

    csv_file = pd.read_csv(relative_file_path + file)
    csv_file["year"] = year
    count = 0

    # print(f"file: {file}\n")

    count += len(csv_file)

    # print(csv_file.columns)
    # print(f"Number of .csv files: {count}, number of rowns in df: {len(csv_file)}")
    # print(csv_file)
    # print the number of rows that have longitude and latitude that are not empty
    # print 5 random lines of the df
    # make new file called {year}.xlsx that saves the df, do not save the index
    new_df = pd.concat([new_df, csv_file])


# rename the column Hiker Journal Link to Hiker Profile Link
new_df.rename(columns={"Hiker Journal Link": "Hiker Profile Link"}, inplace=True)
new_df.rename(columns={"Name": "Actual Name"}, inplace=True)

print(f"new df columns = \n{new_df.columns}")

# cast all values in the year column in new_df to int
new_df["year"] = new_df["year"].astype(int)

merged_df = pd.merge(new_df, df, on=["Hiker trail name", "year"])


sample = merged_df.sample(1)

# print the value in each col alongside the column name
for col in sample.columns:
    print(f"{col}: {sample[col].values[0]}")

print(f"merged df len = \n{len(merged_df)}")
print(f"original df len = \n{len(df)}")


# print each year into its own .xlsx file
for year in years:
    df = merged_df[merged_df["year"] == int(year)]
    df.to_excel(f"../raw_trail_journal_data/xlsx/{year}_v3.xlsx", index=False)
