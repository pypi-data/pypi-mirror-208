use pyo3::prelude::*;
use rand::Rng;
use std::cmp::Ordering;
use std::io;

#[pyfunction]
fn guess_the_number() {
    println!("Guess the number!");

    let secret_number = rand::thread_rng().gen_range(1..101);

    loop {
        println!("Please input your guess.");

        let mut guess = String::new();

        io::stdin()
            .read_line(&mut guess)
            .expect("Failed to read line");

        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };

        println!("You guessed: {}", guess);

        match guess.cmp(&secret_number) {
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too big!"),
            Ordering::Equal => {
                println!("You win!");
                break;
            }
        }
    }
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn windows_control(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(guess_the_number, m)?)?;

    Ok(())
}


// use pyo3::prelude::*;

// #[pyfunction]
// fn add(a: i64, b: i64) -> PyResult<i64> {
//     Ok(a + b)
// }

// #[pyclass]
// struct KeyBoard {
//     #[pyo3(get)]
//     name: String,
// }

// #[pymethods]
// impl KeyBoard {
//     #[new]
//     fn new(name: String) -> Self {
//         KeyBoard { name }
//     }

//     fn test_input(&self, input: String) -> PyResult<String> {
//         Ok(format!("{} {}", self.name, input))
//     }
// }

// #[pymodule]
// fn my_module(_py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_function(wrap_pyfunction!(add, m)?)?;
//     m.add_class::<KeyBoard>()?;

//     Ok(())
// }
