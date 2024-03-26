import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# data = np.load("Data/LD3_3_22_24.npy")
# dark = np.load("Data/dark_current_LD3_3_22_24.npy")

data = np.load("test_data.npy")
dark = np.load("dark_current.npy")

dark = dark[0,:]

print(dark)
print(data)

sum = np.sum(data, axis=0)
print(sum.shape)
print(sum)

# data[0,:,:] = data[0,:,:] - dark[0]
# data[1,:,:] = data[1,:,:] - dark[1]
# data[2,:,:] = data[2,:,:] - dark[2]
# data[3,:,:] = data[3,:,:] - dark[3]

x, y, z = data.shape

max = np.max(data)
min = np.min(data)

fig, ax = plt.subplots(2, 2, figsize=(9, 8))
fig.suptitle("Current Outputs", size = 15)

for col in range(2):
    for row in range(2):
        output = row * 2 + col

        title = ""

        match output:
            case 0:
                title = "Left"
            case 1:
                title = "Top"
            case 2:
                title = "Right"
            case 3:
                title = "Bottom"

        sns.heatmap(data[output, :, :], ax=ax[row, col], cmap='jet', cbar=True, cbar_kws={'pad':0.01, 'shrink':0.8, 'format':'{x:.0e}'},
                    square=True, vmin=min, vmax=max)
        # cbar = ax[row, col].collections[0].colorbar
        # cbar.ax.set_title("Current", size=10)
        
        ax[row, col].set_title(title, size=10)
        ax[row, col].set_xlabel('X', size=10)
        ax[row, col].set_ylabel('Y', size=10)
        ax[row, col].invert_yaxis()

fig.subplots_adjust(wspace=0.3, hspace=0.3)
fig.savefig("Correct Outputs.png")
plt.show()

fig2, ax2 = plt.subplots(1, 1,)
sns.heatmap(sum, ax=ax2, cmap='jet', cbar=True, cbar_kws={'pad':0.01, 'shrink':0.8, 'format':'{x:.0e}'},
                    square=True, vmin=min, vmax=max)

plt.show()