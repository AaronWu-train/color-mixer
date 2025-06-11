import pymixbox
import numpy as np

A = (202, 20, 123)
B = (0, 0, 0)

A_latent = np.array(pymixbox.color.rgb_to_latent(A))
B_latent = np.array(pymixbox.color.rgb_to_latent(B))

C_latent = 0.5 * A_latent + 0.5 * B_latent
C = pymixbox.color.latent_to_rgb(C_latent)

print(f"A: {A}, B: {B}, C: {C}")
