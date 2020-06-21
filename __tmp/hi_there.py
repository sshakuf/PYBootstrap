import time
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.title('Radar map')
tx_on = st.button('TX ON')
st.write(f"TX state {tx_on}")

N = 100
M = 1024

r = np.linspace(0, (M - 1) * 0.15, M).reshape([1, M])
az = np.linspace(-10, 10, N).reshape([N, 1])

x = r * np.sin(az * np.pi / 180)
y = r * np.cos(az * np.pi / 180)

z = np.zeros([N - 1, M - 1])
data = z

fig, ax2 = plt.subplots(1, 1)
quad1 = ax2.pcolorfast(x, y, z, cmap='rainbow', vmin=0, vmax=5)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
# ax2.axis('equal')
ax2.set_xlim([-50, 50])
ax2.set_ylim([0, 170])
fig.patch.set_facecolor('#E0E0E0')
r = 0
the_plot = st.pyplot(plt)

while True:
    data[0:N - 1, 0:8191] = np.random.random([N - 1, M - 1])
    r = (r + 20) % 1200
    data[40:60, r:r+10] = 5

    quad1.set_array(data.ravel())
    the_plot.pyplot(plt)

# progress_bar = st.sidebar.progress(0)
# status_text = st.sidebar.empty()
# last_rows = np.random.randn(1, 1)
# chart = st.line_chart(last_rows)
# st.button
