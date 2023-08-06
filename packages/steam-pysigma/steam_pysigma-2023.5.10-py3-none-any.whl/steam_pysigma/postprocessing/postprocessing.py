

"""
Methods for postprocessing the txt results from a COMSOL - SIGMA simulation

"""
import pandas as pd


def export_B_field_txt_to_map2d(path_map2d_roxie, path_result_txt_Bx, path_result_txt_By, path_new_file):
    """
    Copy content of reference map2d file and overwrites Bx and By values which are replaced values from
    comsol output txt file and writes to a new map2d file.
    :param path_map2d: Path to reference map2d from which all values apart from Bx and By is copied from
    :param path_result: Comsol output txt file with evaluated B-field
    :param path_new_file: Path to new map2d file where new B-field is stored
    :return:
    """
    df_reference = pd.read_csv(path_map2d_roxie, delim_whitespace=True)
    with open(path_result_txt_Bx) as file:  # opens a text file
        lines = [line.strip().split() for line in file if not "%" in line]  # loops over each line

    df_txt_Bx = pd.DataFrame(lines, columns=["x", "y", "Bx"])

    df_txt_Bx = df_txt_Bx.apply(pd.to_numeric)

    with open(path_result_txt_By) as file:  # opens a text file
        lines = [line.strip().split() for line in file if not "%" in line]  # loops over each line

    df_txt_By = pd.DataFrame(lines, columns=["x", "y", "By"])
    df_txt_By = df_txt_By.apply(pd.to_numeric)

    # Verify all evaluate field at same coordinates!

    x_tol, y_tol = 1e-10, 1e-10
    x_ref, y_ref = df_reference['X-POS/MM'] / 1000, df_reference['Y-POS/MM'] / 1000

    if ((x_ref - df_txt_Bx['x']).abs().max() < x_tol) and \
            ((x_ref - df_txt_By['x']).abs().max() < x_tol) and \
            ((y_ref - df_txt_Bx['y']).abs().max() < y_tol) and \
            ((y_ref - df_txt_By['y']).abs().max() < y_tol):
        print("All dataframes have the same x and y coordinates.")
    else:
        raise ValueError("Error: Not all dataframes have the same x and y coordinates. Can't compare map2ds!")

    # Create new map2d
    with open(path_new_file, 'w') as file:
        file.write("  BL.   COND.    NO.    X-POS/MM     Y-POS/MM    BX/T       BY/T"
                   "      AREA/MM**2 CURRENT FILL FAC.\n\n")
        content = []
        for index, row in df_reference.iterrows():
            bl, cond, no, x, y, Bx, By, area, curr, fill, fac = row
            bl = int(bl)
            cond = int(cond)
            no = int(no)
            x = f"{x:.4f}"
            y = f"{y:.4f}"
            Bx = df_txt_Bx["Bx"].iloc[index]
            Bx = f"{Bx:.4f}"
            By = df_txt_By["By"].iloc[index]
            By = f"{By:.4f}"
            area = f"{area:.4f}"
            curr = f"{curr:.2f}"
            fill = f"{fill:.4f}"
            content.append(
                "{0:>6}{1:>6}{2:>7}{3:>13}{4:>13}{5:>11}{6:>11}{7:>11}{8:>9}{9:>8}\n".format(bl, cond, no, x, y, Bx,
                                                                                             By,
                                                                                             area, curr, fill))
        file.writelines(content)