import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image

def adjust_brightness(image, brightness):
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)
    return image

def adjust_contrast(image, contrast):
    image = image.convert("RGB")  
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)
    return image

def adjust_sharpness(image, sharpness):
    img_array = np.array(image)
    img_sharpness = cv2.filter2D(img_array, -1, np.array([[-sharpness, -sharpness, -sharpness],
                                                          [-sharpness, 1 + 8 * sharpness, -sharpness],
                                                          [-sharpness, -sharpness, -sharpness]]))
    image = Image.fromarray(img_sharpness)
    return image

def adjust_hue(image, delta):
    img_np = np.array(image)
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    hsv[:, :, 0] = (hsv[:, :, 0] + delta) % 180
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    image = Image.fromarray(img_np)
    return image

def adjust_gamma(image, gamma):
    image = image.convert("RGB") 
    gamma_correction = lambda value: int(((value / 255.0) ** gamma) * 255)
    image = image.point(gamma_correction)
    return image

def stretch_rgb(image):
    img_np = np.array(image).astype('float32') / 255.0  
    for i in range(3):
        img_np[:,:,i] = cv2.equalizeHist((img_np[:,:,i] * 255).astype('uint8')) / 255.0
    image = Image.fromarray(np.round(img_np * 255).astype('uint8'))
    return image

def stretch_rgb_clahe(image):
    img_np = np.array(image).astype('float32') / 255.0  
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8,8))
    for i in range(3):
        img_np[:,:,i] = clahe.apply((img_np[:,:,i] * 255).astype('uint8')) / 255.0
    image = Image.fromarray(np.round(img_np * 255).astype('uint8'))
    return image

def color_hist(image):
    img = np.asarray(image.convert("RGB")).reshape(-1, 3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    plt.xlim(0, 255)
    st.pyplot(plt)
    fig = plt.gcf()
    plt.close()
    return fig

def main():
    st.set_page_config(layout = "wide")
    st.title("画像変換")
    st.write("## 画像のパラメータ変換")
        
    # 画像のアップロード
    uploaded_file = st.file_uploader("画像を選択してください", type=["jpg", "jpeg", "png"])
    # 画像の保存先のパス
    # パスを入力するテキストボックスを表示
    path = st.text_input("出力画像を保存するディレクトリのパスを入力してください")
    # 入力されたパスを表示
    st.write("入力されたパス:", path)
    # 等分で分割
    col1, col2, col3 = st.columns(3)

    if uploaded_file is not None:
        # アップロードされた画像を開く
        img = Image.open(uploaded_file)

        

        with col1:
            # 変換オプションの選択
            brightness_option = st.checkbox("輝度調整(スライディング)：倍率")
            contrast_option = st.checkbox("コントラスト調整(伸長操作)：倍率")
            equalization_option = st.checkbox("平坦化")
            local_equalization_option = st.checkbox("局所平坦化")
            gamma_option = st.checkbox("ガンマ補正：ガンマ値")        
            sharpness_option = st.checkbox("シャープネス調整：シャープネス度")
            hue_option = st.checkbox("色相変換：彩度・明度")
            
         # 画像の表示
        with col2:
            st.image(img, caption='アップロードされた画像', use_column_width=True)
            fig = color_hist(img)

            if st.button("保存1"):
                # 画像の変換処理
                # 画像の保存名を作成
                save_name = uploaded_file.name
                # 画像を保存
                save_path_img = f"{path}/{save_name}"
                save_path_hist = f"{path}/{save_name}_histgram.png"
                img.save(save_path_img)
                st.write("画像を保存しました：", save_path_img)
                fig.savefig(save_path_hist)
                st.write("ヒストグラムを保存しました：", save_path_hist)
        with col1:
            if brightness_option or sharpness_option or hue_option or contrast_option or gamma_option or equalization_option or local_equalization_option:
                # 輝度変換
                if brightness_option:
                    brightness = st.slider("輝度調整", 0.0, 2.0, 1.0, 0.1)
                    img = adjust_brightness(img, brightness)
                else:
                    brightness = "-"

                # シャープネス変換
                if sharpness_option:
                    sharpness = st.slider("シャープネス調整", -2.0, 2.0, 0.0, 0.1)
                    img = adjust_sharpness(img, sharpness)
                else:
                    sharpness = "-"

                # 色相変換
                if hue_option:
                    delta = st.slider("色相調整", 0, 180, 0)
                    img = adjust_hue(img, delta)               
                else:
                    delta = "-"

                # コントラスト変換
                if contrast_option:
                    contrast = st.slider("コントラスト調整", 0.0, 2.0, 1.0, 0.1)
                    img = adjust_contrast(img, contrast)             
                else:
                    contrast = "-"

                # ガンマ補正
                if gamma_option:
                    gamma = st.slider("ガンマ補正", 0.1, 5.0, 1.0, 0.1)
                    img = adjust_gamma(img, gamma)
                else:
                    gamma = "-"

                # 平坦化
                if equalization_option:
                    img = stretch_rgb(img)

                # 局所平坦化
                if local_equalization_option:
                    img = stretch_rgb_clahe(img)

                with col3:
                    # 変換後の画像の表示
                    st.image(img, caption='変換後の画像',use_column_width=True)

                    # RGBヒストグラムを表示
                    fig = color_hist(img)

            else:
                st.write("少なくとも1つの変換を選択してください。")

        with col3:
            if brightness_option or sharpness_option or hue_option or contrast_option or gamma_option or equalization_option or local_equalization_option:
                if st.button("保存2"):
                        # 画像の変換処理
                        # 画像の保存名を作成
                        save_name_2 = f"{uploaded_file.name}_輝{brightness}_コ{contrast}_色{delta}_シ{sharpness}_ガ{gamma}_平{equalization_option}_局{local_equalization_option}"
                        # 画像を保存
                        save_path_img_2 = f"{path}/{save_name_2}.png"
                        save_path_hist_2 = f"{path}/{save_name_2}_histgram.png"
                        img.save(save_path_img_2)
                        st.write("変換後画像を保存しました：", save_path_img_2)
                        fig.savefig(save_path_hist_2)
                        st.write("変換後ヒストグラムを保存しました：", save_path_hist_2)
                
                st.text("必ず保存1と保存2の操作を行ってから押してください")
                if st.button("4枚を1枚にして保存"):

                    # 変換前の画像の情報
                    save_name = uploaded_file.name
                    save_path_img = f"{path}/{save_name}"
                    save_path_hist = f"{path}/{save_name}_histgram.png"
                    # 変換後の画像の情報
                    save_name_2 = f"{uploaded_file.name}_輝{brightness}_コ{contrast}_色{delta}_シ{sharpness}_ガ{gamma}_平{equalization_option}_局{local_equalization_option}"
                    save_path_img_2 = f"{path}/{save_name_2}.png"
                    save_path_hist_2 = f"{path}/{save_name_2}_histgram.png"

                    # 4枚の画像ファイルパスを指定
                    image_paths = [save_path_img, save_path_img_2, save_path_hist, save_path_hist_2]

                    # 画像を読み込み
                    images = [Image.open(path) for path in image_paths]

                    # 画像サイズを取得
                    width, height= images[0].size
                    width_hist, height_hist= images[3].size

                    # 結合後の画像サイズを計算
                    combined_width = width * 2  # 2枚横に結合する場合
                    combined_height = height + height_hist  # 2枚縦に結合する場合

                    # 結合後の画像を作成
                    combined_image = Image.new('RGB', (combined_width, combined_height))

                    # 画像を結合して配置
                    for i in range(len(images)):
                        x = i % 2 * width  # 横の位置を計算
                        y = i // 2 * height  # 縦の位置を計算
                        combined_image.paste(images[i], (x, y))
                        

                    # 画像を保存
                    save_path_combined = f"{path}/{save_name_2}_combined.jpg"
                    combined_image.save(save_path_combined)
                    st.write("4枚を結合した画像を保存しました:", save_path_combined)

                                            

main()
