import streamlit as st
from PIL import Image
import io

# Convert encoding data into 8-bit binary form using ASCII value of characters


def genData(data):
    newd = []
    for i in data:
        newd.append(format(ord(i), '08b'))
    return newd

# Pixels are modified according to the 8-bit binary data and finally returned


def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):
        pix = [value for value in imdata.__next__()[:3] +
               imdata.__next__()[:3] +
               imdata.__next__()[:3]]

        for j in range(0, 8):
            if (datalist[i][j] == '0' and pix[j] % 2 != 0):
                pix[j] -= 1
            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                if (pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1

        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if (pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1
        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]


def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1


def encode_image():
    uploaded_image = st.file_uploader(
        "Upload an image", type=["jpg", "png", "jpeg", "gif", "bmp", "webp"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        data = st.text_area("Enter data to be encoded:")
        if st.button("Encode"):
            if len(data) == 0:
                st.error("Data is empty. Please enter data to encode.")
            else:
                # Check if the image is large enough to encode the data
                # Each character needs 3 pixels
                required_pixels = len(data) * 3
                if len(image.getdata()) < required_pixels:
                    st.error(
                        "Image is too small to encode the data. Please choose a larger image.")
                else:
                    newimg = image.copy()
                    encode_enc(newimg, data)

                    st.image(newimg, caption="Encoded Image",
                             use_column_width=True)
                    st.success("Image encoded successfully.")

                    # Save the encoded image to a bytes buffer
                    encoded_image_buffer = io.BytesIO()
                    newimg.save(encoded_image_buffer, format="PNG")
                    encoded_image_data = encoded_image_buffer.getvalue()

                    # Create a download button for the encoded image
                    st.download_button(
                        label="Download Encoded Image",
                        data=encoded_image_data,
                        file_name="encoded_image.png",
                        key="download_encoded_image",
                    )


def decode_image():
    uploaded_encoded_image = st.file_uploader(
        "Upload an image", type=["jpg", "png", "jpeg", "gif", "bmp", "webp"])

    if uploaded_encoded_image is not None:
        encoded_image = Image.open(uploaded_encoded_image)
        st.image(encoded_image, caption="Uploaded Encoded Image",
                 use_column_width=True)

        if st.button("Decode"):
            # Pass the encoded image to the decode function
            decoded_data = decode(encoded_image)
            st.text(f"Decoded Data: {decoded_data}")


def decode(encoded_image):
    imgdata = iter(encoded_image.getdata())
    data = ''

    while True:
        pixels = [value for value in imgdata.__next__()[:3] +
                  imgdata.__next__()[:3] +
                  imgdata.__next__()[:3]]

        # String of binary data
        binstr = ''

        for i in pixels[:8]:
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            break  # Message is over

    return data


def metadata_analysis():
    uploaded_image = st.file_uploader(
        "Upload an image", type=["jpg", "png", "jpeg", "gif", "bmp", "webp", "avif"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Metadata Analysis for the image
        metadata = image.info
        st.subheader("Metadata Analysis for Image:")
        st.write(metadata)


def main():
    st.title("Steganography App")

    # Create a sidebar for option selection
    st.sidebar.image("logo.jpg", use_column_width=True)

    option = st.sidebar.selectbox(
        "Choose an option:", ("Encode", "Decode", "Metadata Analysis"))

    if option == "Encode":
        encode_image()
    elif option == "Decode":
        decode_image()
    elif option == "Metadata Analysis":
        metadata_analysis()


if __name__ == '__main__':
    main()

# streamlit run merge.py