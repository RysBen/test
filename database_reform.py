
# replace
df['A'].replace(to_replace=r"\[\d+\]", \
                value="\g<1>\n", \
                regex=True, \
                inplace=True)

# reform
df.drop('Country', axis=1).join(df['Country'].str.split('/', expand=True).stack().reset_index(level=1, drop=True).rename('Country'))

# multi pats
