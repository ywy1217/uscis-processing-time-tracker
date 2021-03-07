import matplotlib.backends.backend_pdf as mpl_pdf
import matplotlib.pyplot as plt

color_map = {'Received': 'gray',
             'Processing': 'yellow',
             'Fingerprint': 'blue',
             'RFE': 'cyan',
             'Interview': 'teal',
             'Approved': 'lime'}


def save_pdf(savePath):
    pdf = mpl_pdf.PdfPages(savePath)
    for fig_k in range(1, plt.figure().number):
        pdf.savefig(fig_k)
    pdf.close()
    print('Saved PDF report at:', savePath)
