# Berkeley Admissions: Actual vs. Expected?

## Live Dashboard
https://uc-dashboard-construction-yukti-durbha-6tgvyefcgabvfnb52rpek5.streamlit.app/

## Research Question

From 2023–2025, which Bay Area public high schools consistently
exceeded their expected UC Berkeley admission rate?

## Key Finding

Mission Senior High School was the strongest consistent outperformer.

Across Fall 2023–2025, Mission Senior had 244 Berkeley applicants and
102 admits, producing an actual admit rate of 41.8%.

Its applicant-weighted expected admit rate was 16.8%, meaning it
outperformed expectation by approximately **25.1 percentage points**.

Mission Senior also exceeded its expected admit rate in each of the
three individual years studied.

## Methodology

I analyzed the provided `dashboard_data.csv` dataset and focused on Bay
Area public high schools with UC Berkeley applicants from Fall 2023
through Fall 2025.

The dataset includes an `expected_admit_rate` based on a-g completion,
poverty, applicant GPA, and school size. I compared each school's actual
Berkeley admit rate with this expected baseline.

For multi-year comparisons, I aggregated actual admits and expected
admits using applicant counts rather than simply averaging annual admit
rates.

To qualify as a consistent outperformer, a school had to:

- Have observations in all three years from 2023–2025
- Have at least 50 total Berkeley applicants
- Exceed its expected admit rate in each of the three years

The 50-applicant threshold reduces volatility caused by very small
applicant pools.

Schools are distinguished using their ATP school code because multiple
California high schools can share the same name.

## Limitations

The dataset contains aggregated high-school-level data rather than
individual applicant records. These results identify school-level
patterns and should not be interpreted as causal effects or predictions
of an individual student's chance of admission.

## Dashboard

The Streamlit dashboard includes:

1. Actual vs. expected Berkeley admit rates
2. The highest consistent outperformers
3. An interactive school explorer showing annual actual versus expected rates

## Data Sources

UC Admissions Data Challenge data derived from the University of
California Information Center and California Department of Education.
