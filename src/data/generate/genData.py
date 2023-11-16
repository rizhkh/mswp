import matplotlib.pyplot as plt

class generateData:

    # Data from Strategy One
    def strategy_one(self):
        plt.figure(figsize=(7, 4))  # 10 is width, 7 is height
        # plt.plot([0.0, 0.2, 0.4, 0.6, 0.8, 1],
        #          [9,  8,     9,   6,   6,   5], 'go', label='Success', linestyle='-')  # success rate

        plt.plot([8, 10, 12, 16, 24, 32, 40], # mines
                 [6, 6,  6,  7,  10, 12, 8], 'go', label='Flagged Cells', linestyle='-')  # success rate

        plt.plot([8, 10, 12, 16, 24, 32, 40],
                 [2,  4, 6, 9,   14,   20,   32], 'ro', label='Cells opened', linestyle='-')  # blocked path
        plt.title(' Improved Algorithm')
        plt.xlabel(" Mines ")
        # plt.xlim(0, 10)
        # plt.ylim(0, 12)
        plt.xlim(0, 50)
        plt.ylim(0, 50)
        plt.legend(loc='best')
        plt.show()

    # Data from Strategy Two
    def strategy_Two(self):
        plt.figure(figsize=(7, 4))  # 10 is width, 7 is height
        # plt.plot([0.0, 0.2, 0.4, 0.6, 0.8, 1],
        #          [9,  8,     9,   6,   6,   5], 'go', label='Success', linestyle='-')  # success rate

        plt.plot([8, 10, 12, 16, 24, 32, 40], # mines
                 [0, 3,  1,  5,  7, 6, 2], 'go', label='Flagged Cells', linestyle='-')  # success rate

        plt.plot([8, 10, 12, 16, 24, 32, 40],
                 [8,  7, 11, 11,17, 26, 28], 'ro', label='Cells opened', linestyle='-')  # blocked path
        plt.title(' Basic Algorithm')
        plt.xlabel(" Mines ")
        # plt.xlim(0, 10)
        # plt.ylim(0, 12)
        plt.xlim(0, 50)
        plt.ylim(0, 50)
        plt.legend(loc='best')
        plt.show()