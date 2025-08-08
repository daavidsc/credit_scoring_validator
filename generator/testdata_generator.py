# generator/testdata_generator.py

import pandas as pd
from faker import Faker
import random


# Define the URLs for the forenames and surnames CSV files
forenames_url = "https://raw.githubusercontent.com/sigpwned/popular-names-by-country-dataset/main/common-forenames-by-country.csv"
surnames_url = "https://raw.githubusercontent.com/sigpwned/popular-names-by-country-dataset/main/common-surnames-by-country.csv"

# Load the data from each URL into two separate pandas DataFrames
df_forenames = pd.read_csv(forenames_url)
df_surnames = pd.read_csv(surnames_url)

# Rename 'Romanized Name' to 'Name' for consistency
df_forenames.rename(columns={'Romanized Name': 'Name'}, inplace=True)
df_surnames.rename(columns={'Romanized Name': 'Name'}, inplace=True)


forenames_by_country_gender = df_forenames.groupby(['Country', 'Gender'])['Name'].apply(list).to_dict()
surnames_by_country = df_surnames.groupby('Country')['Name'].apply(list).to_dict()


def generate_random_person(forenames_by_country_gender, surnames_by_country, nationality_distribution):
    """Generates a random person with full name, nationality, and gender based on distribution."""

    # Select nationality based on the provided distribution
    nationality = random.choices(list(nationality_distribution.keys()), weights=nationality_distribution.values(), k=1)[0]


    countries = list(surnames_by_country.keys())
    # while True:
    #     nationality = random.choice(countries)
    gender = random.choice(['M', 'F'])
    #    if (nationality, gender) in forenames_by_country_gender and surnames_by_country.get(nationality):
    #        break

    # Ensure selected nationality exists in name data, otherwise fallback
    if (nationality, gender) not in forenames_by_country_gender or nationality not in surnames_by_country:
        # Fallback to a nationality that exists in the data if the selected one doesn't
        valid_nationalities = [nat for nat in countries if (nat, gender) in forenames_by_country_gender and nat in surnames_by_country]
        if valid_nationalities:
            nationality = random.choice(valid_nationalities)
        else:
             # If no valid nationality is found for the chosen gender, try the other gender
            gender = 'F' if gender == 'M' else 'M'
            valid_nationalities = [nat for nat in countries if (nat, gender) in forenames_by_country_gender and nat in surnames_by_country]
            if valid_nationalities:
                 nationality = random.choice(valid_nationalities)
            else:
                 # If still no valid nationality, return None or raise an error
                 return None # Or handle this case as needed


    forename = random.choice(forenames_by_country_gender[(nationality, gender)])
    surname = random.choice(surnames_by_country[nationality])
    full_name = f"{forename} {surname}"

    return {
        'full_name': full_name,
        'nationality': nationality,
        'gender': 'male' if gender == 'M' else 'female' # Map 'M'/'F' to 'male'/'female'
    }



def generate_test_data(num_records=1, locales=['de_DE'], nationality_distribution=None):
    """Generates a list of dictionaries with fake data based on a predefined structure."""
    fake = Faker(locales)
    data = []
    for _ in range(num_records):
        record = {}

        # Use generate_random_person to get name, nationality, and gender
        person_data = generate_random_person(forenames_by_country_gender, surnames_by_country, nationality_distribution)

        # Handle the case where generate_random_person returns None
        if person_data is None:
            continue # Skip this record if no valid nationality was found


        record["name"] = person_data['full_name']
        record["gender"] = person_data['gender']
        
        # Randomly change about 1.5% of people to non_binary
        if random.random() < 0.015:
            record["gender"] = "non_binary"
        
        record["nationality"] = person_data['nationality']
        nationality = record["nationality"]
        possible_ethnicities = nationality_ethnicity_mapping.get(nationality, [('other', 1.0)]) # Default to 'other' if nationality not in map
        ethnicity_choices, weights = zip(*possible_ethnicities)
        record["ethnicity"] = random.choices(ethnicity_choices, weights=weights, k=1)[0]

        record["age"] = fake.random_int(min=18, max=80)
        # Adjust mean income based on age
        base_mean_income = 20000
        age_effect = (record["age"] - 18) * 2000  # Simple linear increase with age
        mean_income = base_mean_income + age_effect
        std_dev_income = 15000 # Example standard deviation (reduced for potentially less spread)

        generated_income = int(random.gauss(mean_income, std_dev_income))
        # Ensure income is within the desired range
        record["income"] = max(20000, min(150000, generated_income))


        # Adjust employment status distribution based on age
        age = record["age"]
        if age < 60:
            employment_status_distribution = [
                ('employed', 0.80),
                ('unemployed', 0.05),
                ('self_employed', 0.10),
                ('student', 0.05),
                ('retired', 0.0) # Very low chance of being retired at young age
            ]
        elif age < 65:
             employment_status_distribution = [
                ('employed', 0.68),
                ('unemployed', 0.05),
                ('self_employed', 0.10),
                ('student', 0.02),
                ('retired', 0.15) # Increased chance of being retired
            ]
        else:
             employment_status_distribution = [
                ('employed', 0.09),
                ('unemployed', 0.02),
                ('self_employed', 0.03),
                ('student', 0.01),
                ('retired', 0.85) # High chance of being retired at older age
            ]


        statuses, weights = zip(*employment_status_distribution)
        record["employment_status"] = random.choices(statuses, weights=weights, k=1)[0]

        record["existing_loans"] = fake.random_int(min=0, max=5)

        # Generate loan_amount using a Gaussian distribution and ensure it's within the range
        if record["existing_loans"] > 0:
            # Adjust mean loan amount based on the number of existing loans
            mean_loan_amount = 5000 + (record["existing_loans"] * 3000) # Increase mean loan amount with more loans
            std_dev_loan_amount = 5000 # Example standard deviation
            generated_loan_amount = int(random.gauss(mean_loan_amount, std_dev_loan_amount))
            # Ensure loan_amount is within the desired range
            record["loan_amount"] = max(500, min(50000, generated_loan_amount))
        else:
            record["loan_amount"] = 0


        record["credit_limit"] = fake.random_int(min=0, max=100000)
        record["used_credit"] = fake.random_int(min=0, max=record["credit_limit"]) # Ensure used_credit <= credit_limit

        # Use random.choices for weighted selection of payment_defaults
        payment_defaults_distribution = [(0, 0.8), (1, 0.1), (2, 0.05), (3, 0.05)]
        defaults, weights = zip(*payment_defaults_distribution)
        record["payment_defaults"] = random.choices(defaults, weights=weights, k=1)[0]

        # Use random.choices for weighted selection of credit_inquiries_last_6_months
        credit_inquiries_distribution = [(0, 0.4), (1, 0.25), (2, 0.15), (3, 0.1), (4, 0.05), (5, 0.03), (6, 0.02)]
        inquiries, weights = zip(*credit_inquiries_distribution)
        record["credit_inquiries_last_6_months"] = random.choices(inquiries, weights=weights, k=1)[0]

        # Use random.choices for weighted selection of housing_status
        housing_status_distribution = [('owner', 0.45), ('renter', 0.45), ('subsidized_housing', 0.05), ('other', 0.05)]
        housing_statuses, weights = zip(*housing_status_distribution)
        record["housing_status"] = random.choices(housing_statuses, weights=weights, k=1)[0]

        record["address_stability_years"] = fake.random_int(min=0, max=record["age"]) # Ensure address_stability_years <= age
        # Use random.choices for weighted selection of household_size
        household_size_distribution = [(1, 0.3), (2, 0.3), (3, 0.2), (4, 0.1), (5, 0.05), (6, 0.03), (7, 0.02)]
        household_sizes, weights = zip(*household_size_distribution)
        record["household_size"] = random.choices(household_sizes, weights=weights, k=1)[0]


        # Ensure employment_duration_years <= age - 16 (approximate working age start)
        # Set employment duration to 0 for retired, students, and unemployed
        if record["employment_status"] in ['retired', 'student', 'unemployed']:
            record["employment_duration_years"] = 0
        else:
            record["employment_duration_years"] = fake.random_int(min=0, max=record["age"]-16 if record["age"] >= 16 else 0)

        # Use random.choices for weighted selection of disability_status
        disability_status_distribution = [('none',0.9), ('registered_disability',0.04), ('severe_disability',0.06)]
        disability_statuses, weights = zip(*disability_status_distribution)
        record["disability_status"] = random.choices(disability_statuses, weights=weights, k=1)[0]

        # Use random.choices for weighted selection of education_level
        education_level_distribution = [
            ('no_formal_education', 0.02), 
            ('lower_secondary_education', 0.15), 
            ('intermediate_secondary_education', 0.25), 
            ('upper_secondary_education', 0.20), 
            ('vocational_training', 0.25), 
            ('bachelor_degree', 0.08), 
            ('master_degree', 0.04), 
            ('doctoral_degree', 0.01)
        ]
        education_levels, weights = zip(*education_level_distribution)
        record["education_level"] = random.choices(education_levels, weights=weights, k=1)[0]

        # Use random.choices for weighted selection of marital_status
        marital_status_distribution = [('single', 0.30), ('married', 0.47), ('registered_partnership', 0.06), ('divorced', 0.10), ('widowed', 0.07)]
        marital_statuses, weights = zip(*marital_status_distribution)
        record["marital_status"] = random.choices(marital_statuses, weights=weights, k=1)[0]

        record["postal_code"] = fake.postcode().zfill(5)  # Ensure 5 digits with leading zeros
        record["language_preference"] = 'de'

        data.append(record)
    return data

sample_size = 30


nationality_ethnicity_mapping = {
    # Europe
    'DE': [('white', 0.9), ('other', 0.05), ('hispanic', 0.02), ('asian', 0.02), ('black', 0.01)],  # Germany
    'LZ': [('white', 0.9), ('other', 0.05), ('hispanic', 0.02), ('asian', 0.02), ('black', 0.01)],  # Luxemburg
    'FR': [('white', 0.8), ('black', 0.1), ('other', 0.05), ('asian', 0.03), ('hispanic', 0.02)],  # France
    'GB': [('white', 0.85), ('asian', 0.07), ('black', 0.03), ('other', 0.03), ('hispanic', 0.02)],  # United Kingdom
    'IT': [('white', 0.95), ('other', 0.03), ('black', 0.01), ('asian', 0.01)],  # Italy
    'ES': [('white', 0.9), ('hispanic', 0.05), ('other', 0.03), ('black', 0.01), ('asian', 0.01)],  # Spain
    'PL': [('white', 0.98), ('other', 0.01), ('asian', 0.01)],  # Poland
    'IE': [('white', 0.97), ('other', 0.02), ('asian', 0.01)],  # Ireland
    'SE': [('white', 0.9), ('other', 0.05), ('black', 0.02), ('asian', 0.02), ('hispanic', 0.01)],  # Sweden
    'AT': [('white', 0.9), ('other', 0.08), ('asian', 0.02)],  # Austria
    'BE': [('white', 0.75), ('black', 0.1), ('asian', 0.1), ('other', 0.05)],  # Belgium
    'CH': [('white', 0.8), ('asian', 0.1), ('black', 0.05), ('other', 0.05)],  # Switzerland
    'FI': [('white', 0.92), ('asian', 0.05), ('other', 0.03)],  # Finland
    'NO': [('white', 0.88), ('asian', 0.08), ('black', 0.02), ('other', 0.02)],  # Norway
    'DK': [('white', 0.9), ('asian', 0.07), ('black', 0.02), ('other', 0.01)],  # Denmark
    'HU': [('white', 0.96), ('other', 0.03), ('asian', 0.01)],  # Hungary
    'GR': [('white', 0.9), ('asian', 0.05), ('black', 0.03), ('other', 0.02)],  # Greece
    'PT': [('white', 0.9), ('black', 0.05), ('other', 0.03), ('asian', 0.02)],  # Portugal
    'UA': [('white', 0.95), ('asian', 0.03), ('other', 0.02)],  # Ukraine
    'RU': [('white', 0.9), ('asian', 0.05), ('other', 0.05)],  # Russia
    'TR': [('other', 0.9), ('white', 0.1)], # Turkey - added
    'RO': [('white', 0.95), ('other', 0.05)], # Romania - added
    'HR': [('white', 0.95), ('other', 0.05)], # Croatia - added
    'BG': [('white', 0.9), ('asian', 0.05), ('other', 0.05)], # Bulgaria - added


    # Americas
    'US': [('white', 0.6), ('black', 0.15), ('hispanic', 0.15), ('asian', 0.05), ('native_american', 0.03), ('other', 0.02)],  # United States
    'CA': [('white', 0.7), ('asian', 0.1), ('hispanic', 0.05), ('black', 0.05), ('native_american', 0.05), ('other', 0.05)],  # Canada
    'BR': [('hispanic', 0.5), ('white', 0.3), ('black', 0.15), ('asian', 0.03), ('native_american', 0.01), ('other', 0.01)],  # Brazil
    'MX': [('hispanic', 0.8), ('native_american', 0.1), ('white', 0.05), ('other', 0.03), ('asian', 0.01), ('black', 0.01)],  # Mexico
    'AR': [('white', 0.85), ('hispanic', 0.1), ('other', 0.03), ('native_american', 0.01), ('black', 0.01)],  # Argentina
    'CL': [('hispanic', 0.9), ('white', 0.05), ('native_american', 0.03), ('other', 0.02)],  # Chile
    'CO': [('hispanic', 0.8), ('white', 0.1), ('black', 0.05), ('native_american', 0.03), ('other', 0.02)],  # Colombia
    'PE': [('hispanic', 0.6), ('native_american', 0.3), ('white', 0.05), ('other', 0.05)],  # Peru
    'VE': [('hispanic', 0.8), ('white', 0.1), ('black', 0.05), ('native_american', 0.03), ('other', 0.02)],  # Venezuela
    'UY': [('white', 0.9), ('hispanic', 0.08), ('black', 0.01), ('other', 0.01)],  # Uruguay
    'PY': [('hispanic', 0.9), ('native_american', 0.05), ('white', 0.03), ('other', 0.02)],  # Paraguay
    'BO': [('hispanic', 0.7), ('native_american', 0.25), ('white', 0.03), ('other', 0.02)],  # Bolivia

    # Asia
    'CN': [('asian', 0.98), ('other', 0.02)],  # China
    'JP': [('asian', 0.98), ('other', 0.02)],  # Japan
    'IN': [('asian', 0.9), ('other', 0.08), ('white', 0.02)],  # India
    'PK': [('asian', 0.95), ('other', 0.05)],  # Pakistan
    'BD': [('asian', 0.95), ('other', 0.05)],  # Bangladesh
    'ID': [('asian', 0.95), ('other', 0.05)],  # Indonesia
    'VN': [('asian', 0.98), ('other', 0.02)],  # Vietnam
    'KR': [('asian', 0.99), ('other', 0.01)],  # South Korea
    'TH': [('asian', 0.98), ('other', 0.02)],  # Thailand
    'MY': [('asian', 0.9), ('other', 0.1)],  # Malaysia
    'SG': [('asian', 0.9), ('white', 0.05), ('other', 0.05)],  # Singapore
    'AE': [('asian', 0.7), ('white', 0.15), ('black', 0.1), ('other', 0.05)],  # UAE
    'SA': [('asian', 0.6), ('white', 0.3), ('black', 0.05), ('other', 0.05)],  # Saudi Arabia
    'IR': [('asian', 0.9), ('other', 0.1)],  # Iran
    'SY': [('other', 0.8), ('asian', 0.1), ('white', 0.1)], # Syria - added
    'AF': [('asian', 0.9), ('other', 0.1)], # Afghanistan - added


    # Africa
    'NG': [('black', 0.95), ('other', 0.05)],  # Nigeria
    'ZA': [('black', 0.7), ('white', 0.1), ('colored', 0.1), ('asian', 0.05), ('other', 0.05)],  # South Africa
    'EG': [('white', 0.9), ('other', 0.1)],  # Egypt
    'KE': [('black', 0.97), ('asian', 0.02), ('other', 0.01)],  # Kenya
    'GH': [('black', 0.98), ('other', 0.02)],  # Ghana
    'DZ': [('white', 0.9), ('other', 0.1)],  # Algeria
    'MA': [('white', 0.9), ('other', 0.1)],  # Morocco

    # Oceania
    'AU': [('white', 0.85), ('asian', 0.1), ('other', 0.03), ('native_american', 0.01), ('black', 0.01)],  # Australia
    'NZ': [('white', 0.7), ('asian', 0.15), ('pacific_islander', 0.1), ('native_american', 0.03), ('other', 0.02)],  # New Zealand
    'FJ': [('pacific_islander', 0.6), ('asian', 0.3), ('white', 0.05), ('other', 0.05)],  # Fiji
    'PG': [('pacific_islander', 0.9), ('asian', 0.05), ('other', 0.05)],  # Papua New Guinea
    'WS': [('pacific_islander', 0.95), ('other', 0.05)],  # Samoa
    'TO': [('pacific_islander', 0.98), ('other', 0.02)],  # Tonga
}


nationality_distribution = {
    # German nationals
    'DE': 0.7,  # 70% German
    # EU countries (15%)
    'TR': 0.04, # Turkey (largest immigrant group in Germany)
    'PL': 0.03, # Poland
    'IT': 0.02, # Italy
    'RO': 0.02, # Romania
    'GR': 0.01, # Greece
    'HR': 0.01, # Croatia
    'BG': 0.01, # Bulgaria
    'ES': 0.01, # Spain
    'FR': 0.01, # France

    # Non-EU countries (15%)
    'SY': 0.03, # Syria (large refugee population)
    'RU': 0.02, # Russia
    'UA': 0.02, # Ukraine
    'US': 0.01, # United States
    'CN': 0.01, # China
    'IN': 0.01, # India
    'VN': 0.01, # Vietnam
    'IR': 0.01, # Iran
    'AF': 0.01, # Afghanistan
    'NG': 0.01, # Nigeria
}


# Calculate the current sum of weights
current_sum = sum(nationality_distribution.values())


if current_sum < 1.0:
    remaining_percentage = 1.0 - current_sum
    # Distribute the remaining percentage among 'other' or adjust existing weights
    # For this example, I'll just print a warning. In a real scenario, you'd adjust weights.
    print(f"Warning: Nationality distribution weights sum to {current_sum}. They should sum to 1.0.")
    print("Please adjust the weights to ensure the correct distribution.")


df = pd.DataFrame()
# Generate data with the specified nationality distribution
test_data = generate_test_data(num_records=sample_size, locales='de_DE', nationality_distribution=nationality_distribution)
df = pd.DataFrame(test_data)

# Export the DataFrame as a CSV file
df.to_csv('data/testdata.csv', index=False)



