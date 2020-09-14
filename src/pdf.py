from fpdf import FPDF 

def export_pdf():
    images=[['movies_years.png',38.07, 260.82],['years.png',228.575,171.42],['movies_age.png',150,98],['age.png',600,300]]
    print('Now, we will export a report with the tables and graphs above')
    print('Exporting...')

    pdf = FPDF(unit="pt")      

    pdf.set_xy(100,100)
    pdf.add_page("p")
    pdf.set_font("Helvetica","B",12)
    pdf.cell(120,30, "Report based on Years",ln=1)
    pdf.set_font("Helvetica","",9)
    pdf.cell(120,30, "The next table summarizes the movies recorded every year from 2001-2020:",ln=1)
    pdf.image(f'output/{images[0][0]}',w=images[0][1],h=images[0][2])
    pdf.cell(120,30, "Expressed as a bar plot in the following figure:",ln=1)
    pdf.image(f'output/{images[1][0]}',w=images[1][1],h=images[1][2])


    pdf.add_page("l")
    pdf.set_font("Helvetica","B",12)
    pdf.cell(120,30, "Report based on recommended Ages",ln=1)
    pdf.set_font("Helvetica","",9)
    pdf.cell(120,30, "The next table summarizes the amount of movies per recommended age in each platform:",ln=1)
    pdf.image(f'output/{images[2][0]}',w=images[2][1],h=images[2][2])
    pdf.cell(120,30, "Expressed as a pie plot in the following figure:",ln=1)
    pdf.image(f'output/{images[3][0]}',w=images[3][1],h=images[3][2])

    print('Your report was succesfully exported')


    return pdf.output("output/report.pdf")