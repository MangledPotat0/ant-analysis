/******************************************************************************/
/*                                                                            */
/*   Created: 2022/06/12                                                      */
/*   Last modified: 2022/06/12                                                */
/*                                                                            */
/******************************************************************************/

use std::io;

fn main() {
    let mut filename = String::new();

    println!("Enter filename");
    io::stdin()
        .read_line(&mut filename)
        .expect("Failed to read line");

    println!("Filename: {}", filename);
}
