from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from dipy.io.image import load_nifti, save_nifti
from PIL import Image
from scipy.ndimage import rotate


class Headermsg:
    """Class containing headers for messages during execution of the CLI."""

    info = "\x1b[0;30;44m [INFO] \x1b[0m "
    warn = "\x1b[0;30;43m [WARNING] \x1b[0m "
    error = "\x1b[0;30;41m [ERROR] \x1b[0m "
    success = "\x1b[0;30;42m [SUCCESS] \x1b[0m "
    pointer = "\x1b[5;36;40m>>>\x1b[0m "
    ask = "\x1b[0;30;46m ? \x1b[0m "
    welcome = (
        "\n\x1b[0;30;46m                              \x1b[0m\n"
        + "\x1b[0;30;46m  \x1b[0m                          \x1b[0;30;46m  \x1b[0m\n"
        + "\x1b[0;30;46m  \x1b[0m  \x1b[0;36;40mWelcome to resomapper!\x1b[0m  "
        + "\x1b[0;30;46m  \x1b[0m\n"
        + "\x1b[0;30;46m  \x1b[0m                          \x1b[0;30;46m  \x1b[0m\n"
        + "\x1b[0;30;46m                              \x1b[0m\n"
    )
    new_patient1 = "\x1b[0;30;47m * STUDY *  "
    new_patient2 = " * STUDY * \x1b[0m "
    new_modal = "\x1b[0;30;47m > MODAL > \x1b[0m "


def ask_user(question):
    """Allows asking questions to the user. The expected answers
    are 'y' or 'n', returning True or False, respectively.
    """
    while True:
        answer = input(
            "\n" + Headermsg.ask + question + " [y/n]\n" + Headermsg.pointer
        ).lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print(
                f"\n{Headermsg.error}Por favor, introduce una de las dos opciones. "
                "[y/n]\n"
            )


###############################################################################
# Mask creation
###############################################################################
class Mask:
    def __init__(self, study_subfolder: str) -> None:
        self.study_subfolder = study_subfolder

    def prepare_vol(self, vol_3d):
        """Some modifications are needed on the volume: 270 degrees
        rotation and image flip.
        """
        n_slc = vol_3d.shape[2]  # numer of slices
        vol_prepared = []
        rot_degrees = 270
        for j in range(n_slc):
            ima = vol_3d[:, :, j]
            ima = rotate(ima, rot_degrees)
            ima = np.flip(ima, axis=1)
            ima = ima.astype(np.uint8)

            # change only for better visualization purposes
            scale_percent = 440
            width = int(ima.shape[1] * scale_percent / 100)
            height = int(ima.shape[0] * scale_percent / 100)
            dim = (width, height)
            ima = cv2.resize(ima, dim, interpolation=cv2.INTER_AREA)
            vol_prepared.append(ima)

        return vol_prepared

    def min_max_normalization(self, img):
        new_img = img.copy()
        new_img = new_img.astype(np.float32)

        min_val = np.min(new_img)
        max_val = np.max(new_img)
        new_img = (np.asarray(new_img).astype(np.float32) - min_val) / (
            max_val - min_val
        )
        return new_img

    def click(self, event, x, y, flags, param):
        global status
        global counter
        if event == cv2.EVENT_LBUTTONDOWN:  # left click
            click_pos = [(x, y)]
            param[counter].append(click_pos)
        elif event == cv2.EVENT_RBUTTONDOWN:  # right click
            click_pos = [(x, y)]
            param[counter].append(click_pos)
            status = 0  # finish

    def itera(self, ima, refPT):
        """Shows slices for masking. Left click adds a line and right click
        closes the polygon. Next slice will be showed after right click.
        """
        global counter
        global status
        status = 1

        cv2.namedWindow("Imagen")  # creates a new window
        cv2.setMouseCallback("Imagen", self.click, refPT)

        while True:
            if refPT[counter] == []:
                # shows umodified image first while your vertice list is empty
                cv2.imshow("Imagen", ima)
                # cv2.waitKey(1)
            key = cv2.waitKey(1) & 0xFF
            try:
                if len(refPT[counter]) > 1:  # after two clicks
                    ver = len(refPT[counter])  # saves a point
                    line = refPT[counter][ver - 2 : ver]  # creates a line
                    ima = cv2.line(
                        ima, line[0][0], line[1][0], (255, 255, 255), thickness=2
                    )
                    cv2.imshow("Imagen", ima)
                    cv2.waitKey(1)
                    if key == ord("c") or status == 0:  # if 'c' key or right click
                        cv2.destroyAllWindows()
                        status = 1  # restore to 1
                        counter += 1  # pass to the next slice
                        break
            except IndexError:
                cv2.destroyAllWindows()
                break
        return refPT

    def create_mask(self):
        """Create binary mask for the brain and save it as a nii file."""

        study_name = self.study_subfolder.parts[-2]
        print(
            f"\n{Headermsg.ask}Crea la máscara para el estudio {str(study_name)}"
            " en la ventana emergente.\n"
            "- Click izquierdo: unir las líneas del contorno de selección\n"
            "- Click derecho: cierrar el contorno uniendo primer y último punto\n"
        )

        if "T2E" in str(self.study_subfolder):
            try:
                (nii_data, affine) = load_nifti(
                    self.study_subfolder
                    / f"{self.study_subfolder.parts[-1][4:]}_subscan_0.nii.gz"
                )
            except FileNotFoundError:
                (nii_data, affine) = load_nifti(
                    self.study_subfolder
                    / f"{self.study_subfolder.parts[-1][4:]}.nii.gz"
                )
            nii_data = nii_data[:, :, :, 0]
        else:
            try:
                (nii_data, affine) = load_nifti(
                    self.study_subfolder
                    / f"{self.study_subfolder.parts[-1][3:]}_subscan_0.nii.gz"
                )
            except FileNotFoundError:
                (nii_data, affine) = load_nifti(
                    self.study_subfolder
                    / f"{self.study_subfolder.parts[-1][3:]}.nii.gz"
                )

            if len(np.shape(nii_data)) == 4:
                nii_data = nii_data[:, :, :, 0]
            if "DT" in str(self.study_subfolder):
                # normalise values to 0-255 range
                nii_data = self.min_max_normalization(nii_data) * 255

        x_dim, y_dim = np.shape(nii_data)[:2]  # get real dims
        images = self.prepare_vol(nii_data)

        # list of lists (one list per slice) for storing masks vertexes
        refPT = [[] for _ in range(len(images))]
        global counter
        counter = 0
        for ima in images:
            refPT = self.itera(ima, refPT)

        # shows user their selection and saves a .png file
        n_slc = np.shape(images)[0]
        rows = 2
        cols = int(np.ceil(n_slc / rows))

        fig, ax = plt.subplots(rows, cols, figsize=(10, 7))
        ax = ax.flatten()
        for i in range(n_slc):
            poly = np.array((refPT[i]), np.int32)
            img_copy = np.copy(images[i])
            img_poly = cv2.polylines(
                img_copy, [poly], True, (255, 255, 255), thickness=3
            )
            im = Image.fromarray(img_poly)
            im.save(self.study_subfolder / f"shape_slice_{str(i+1)}.png")

            ax[i].imshow(img_poly, cmap="gray")
            ax[i].set_title(f"Slice {i+1}")
            ax[i].axis("off")

        plt.tight_layout()
        keyboardClick = False
        while not keyboardClick:
            keyboardClick = plt.waitforbuttonpress(0)
        plt.close()

        # creates niimask file
        masks = []
        for i in range(n_slc):
            poly = np.array((refPT[i]), np.int32)
            background = np.zeros(images[i].shape)
            mask = cv2.fillPoly(background, [poly], 1)
            mask = cv2.resize(mask, (x_dim, y_dim), interpolation=cv2.INTER_NEAREST)
            mask = mask.astype(np.int32)
            masks.append(mask)
            # cv2.destroyAllWindows()
        masks = np.asarray(masks)
        masks = masks.transpose(2, 1, 0)

        # saving mask in both method subfolder and subject folder
        # (for reusing mask purposes)
        save_nifti(self.study_subfolder / "mask", masks.astype(np.float32), affine)
        save_nifti(
            Path("/".join(self.study_subfolder.parts[:-1])) / "mask",
            masks.astype(np.float32),
            affine,
        )
