use pyo3::prelude::*;
use thousands::Separable;


#[pyfunction]
pub fn format_currency_string(amount: &str) -> String {
    let amount_separated_by_commas = amount.separate_with_commas();
    let number_of_commas = amount_separated_by_commas.matches(",").count();
    if number_of_commas == 0 {
        return amount_separated_by_commas;
    }

    let trailing_zeros_after_first_comma = ",000".repeat(number_of_commas);
    let trailing_zeros_after_second_comma = ",000".repeat(number_of_commas - 1);

    match number_of_commas {
        1 => return amount_separated_by_commas,
        2..=4 => {
            if amount_separated_by_commas.ends_with(&trailing_zeros_after_first_comma) {
                return replace_all_trailing_zeros_with_word(&amount_separated_by_commas);
            } else if amount_separated_by_commas.ends_with(&trailing_zeros_after_second_comma) {
                return replace_trailing_zeros_with_decimal_and_word(&amount_separated_by_commas); 
            } else {
                return amount_separated_by_commas;
            }
        },
        _ => panic!("Inputted amount is too large"),
    }
}   

fn replace_all_trailing_zeros_with_word(amount: &String) -> String {
    amount.replace(",000,000,000,000", " trillion")
    .replace(",000,000,000", " billion")
    .replace(",000,000", " million")
    .replace(",000", " thousand")
} 

fn replace_trailing_zeros_with_decimal_and_word(amount: &String) -> String {
    let amount_separated_by_commas = amount.separate_with_commas();
    let number_of_commas = amount_separated_by_commas.matches(",").count();
    let trailing_zeros_after_second_comma = ",000".repeat(number_of_commas - 1);

    let amount_without_zeros_after_second_comma = amount.clone().strip_suffix(&trailing_zeros_after_second_comma).unwrap().to_string();
    let amount_with_decimal_point = amount_without_zeros_after_second_comma.replace(",", ".");
    let prefix = amount_with_decimal_point.trim_end_matches("0").to_string();

    match number_of_commas {
        2 => return prefix + " million",
        3 => return prefix + " billion",
        4 => return prefix + " trillion",
        _ => panic!("Input number isn't the right size"),
    }
}


#[pymodule]
fn rust_util(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(format_currency_string, m)?)?;
    Ok(())
}
