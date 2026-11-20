# ASCII Studio Pro

**IMAGE, GIF & VIDEO CONVERTER**

[ Türkçe ](#türkçe) · [ English ](#english)

---

# Türkçe

## Genel Bakış

ASCII Studio Pro; Python ve Tkinter ile geliştirilmiş masaüstü görüntü dönüştürme uygulamasıdır. Statik görselleri, animasyonlu GIF dosyalarını ve videoları ASCII karakterleri veya sembol tabanlı karakter dizileriyle oluşturulmuş görsellere dönüştürür. Arayüzdeki **TR | EN** düğmesiyle Türkçe ve İngilizce arasında geçiş yapılabilir.

## Özellikler

- PNG, JPG, JPEG, WEBP ve BMP görsellerini dönüştürme.
- Animasyonlu GIF dosyalarını kare sürelerini koruyarak dönüştürme.
- Videoları MP4 olarak dışa aktarma; çıktı 30 FPS olarak hazırlanır.
- Kaynak videoda ses varsa dışa aktarılan videoda sesi koruma.
- Görsel, GIF ve video için uygulama içi önizleme.
- GIF oynatma/duraklatma; video oynatma, duraklatma, durdurma ve konumlandırma kontrolleri.
- ASCII çıktı genişliğini ayarlama.
- Yerleşik karakter rampaları ve özel karakter dizisi ekleme.
- Renkli, monokrom ve negatif görünüm seçenekleri.
- İlerleme göstergesi ve dönüştürmeyi iptal etme.
- Dosyayı kaynak türüne uygun biçimde kaydetme.
- Dosyayı doğrudan önizleme alanına sürükleyip bırakma.
- Türkçe ve İngilizce arayüz.

## Desteklenen biçimler

| Kaynak | Uzantılar | Çıktı |
|---|---|---|
| Görsel | `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp` | PNG |
| Animasyon | `.gif` | GIF |
| Video | `.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.m4v` | MP4 |

## Gereksinimler

- Windows önerilir.
- Python 3.10 veya üzeri.
- Tkinter (çoğu Windows Python kurulumunda dahildir).
- FFmpeg desteği `imageio-ffmpeg` paketiyle sağlanır.
- VLC ve `python-vlc` video önizlemesinde ses için isteğe bağlıdır.
- `tkinterdnd2` sürükle-bırak desteği için isteğe bağlıdır.

### Python paketleri

```powershell
py -m pip install --upgrade pip
py -m pip install pillow numpy opencv-python imageio imageio-ffmpeg
```

İsteğe bağlı özellikler:

```powershell
py -m pip install python-vlc tkinterdnd2
```

## Kurulum ve çalıştırma

1. Python 3.10+ kurun.
2. Yukarıdaki gerekli paketleri yükleyin.
3. `ASCII_STUDIO_PRO_FAST.py` dosyasını README ile aynı klasöre koyun.
4. PowerShell veya Komut İstemi'nde klasöre gidip çalıştırın:

```powershell
py ASCII_STUDIO_PRO_FAST.py
```

## Hızlı kullanım

1. Sol sütundaki **Dosya seç** düğmesiyle dosya açın veya dosyayı sağdaki önizleme alanına sürükleyin.
2. ASCII çözünürlüğünü ve karakter setini seçin.
3. İsterseniz özel karakterleri açık tondan koyu tona doğru sıralayarak girin ve **Ekle** düğmesine basın.
4. Renkli, monokrom veya negatif görünümü seçin.
5. **Dönüştür** düğmesine basın. İşlem sırasında **İptal** kullanılabilir.
6. İşlem tamamlandığında **Kaydet** düğmesiyle çıktıyı kaydedin.
7. Arayüz dilini değiştirmek için üstteki **TR | EN** düğmesine basın.

## Karakter setleri ve özel rampalar

Uygulama yerleşik ASCII rampaları ve sembol rampaları sunar. Özel karakter alanına en az iki görünür karakter girilmelidir. Karakterlerin sırası önemlidir: dizi açık tonlardan koyu tonlara doğru sıralanmalıdır. Tekrarlanan karakterler ve boşluklar rampanın yoğunluğunu etkileyebilir.

## Önizleme ve ses

- GIF önizlemesi animasyonludur.
- Video kontrolleri oynat/duraklat, durdur ve zaman çizelgesinde gezinme işlevlerini sunar.
- Video ses önizlemesi için VLC kurulumu gerekebilir.
- VLC bulunmadığında video görüntüsü yine kullanılabilir; ses önizlemesi devre dışı kalabilir.

## Dönüştürme mantığı

Görüntü örneklenerek daha küçük bir parlaklık ızgarasına indirgenir. Her hücrenin parlaklığı seçilen karakter rampasındaki bir karaktere eşlenir. Renkli modda hücre rengi kaynak görüntüden alınır; monokrom modda gri tonlar kullanılır. Negatif modu kaynak parlaklığını tersine çevirir.

## Sorun giderme

- **Tkinter bulunamadı:** Python kurulumunu Tcl/Tk bileşenleriyle onarın veya yeniden kurun.
- **Sürükle-bırak çalışmıyor:** `py -m pip install tkinterdnd2` komutuyla isteğe bağlı paketi yükleyin.
- **Video sesi yok:** VLC Media Player ve `python-vlc` paketinin kurulu olduğunu kontrol edin.
- **Sembol görünmüyor:** İşletim sisteminde sembolü destekleyen bir yazı tipi bulunduğundan emin olun.
- **Video açılamıyor:** Dosyanın bozuk olmadığını ve OpenCV'nin dosya biçimini desteklediğini kontrol edin.

## Proje dosyaları

```text
ASCII-Studio-Pro/
├── ASCII_STUDIO_PRO_FAST.py
├── README_ASCII_STUDIO_PRO.md
└── LICENSE
```

## Lisans

Bu proje **MIT Lisansı** altında yayımlanmak üzere hazırlanmıştır. Dağıtım paketine kök dizinde `LICENSE` adlı dosya ekleyin ve MIT lisans metnini bu dosyada bulundurun. Telif hakkı sahibi ve yıl bilgilerini lisans dosyasında doğru şekilde doldurun.

MIT Lisansı; yazılımın kullanımına, kopyalanmasına, değiştirilmesine, birleştirilmesine, yayımlanmasına, dağıtılmasına, alt lisanslanmasına ve satılmasına izin verir. Lisans bildirimi ve telif hakkı bildirimi yazılımın tüm kopyalarında veya önemli bölümlerinde korunmalıdır. Yazılım herhangi bir garanti olmaksızın, olduğu gibi sunulur.

---

# English

## Overview

ASCII Studio Pro is a desktop image-conversion application built with Python and Tkinter. It converts still images, animated GIFs, and videos into artwork made from ASCII characters or symbol-based character ramps. Use the **TR | EN** button in the interface to switch between Turkish and English.

## Features

- Convert PNG, JPG, JPEG, WEBP, and BMP images.
- Convert animated GIFs while retaining frame timing.
- Export videos as MP4 at 30 FPS.
- Preserve the source video's audio track when an audio stream is available.
- In-app preview for images, GIFs, and videos.
- GIF play/pause and video play, pause, stop, and seek controls.
- Adjustable ASCII output width.
- Built-in character ramps and custom character sequences.
- Colour, monochrome, and negative appearance modes.
- Progress indicator and conversion cancellation.
- Save output in the format associated with the source type.
- Drag and drop files directly onto the preview area.
- Turkish and English user interface.

## Supported formats

| Input | Extensions | Output |
|---|---|---|
| Image | `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp` | PNG |
| Animation | `.gif` | GIF |
| Video | `.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.m4v` | MP4 |

## Requirements

- Windows is recommended.
- Python 3.10 or newer.
- Tkinter (included with most Windows Python installations).
- FFmpeg support is provided by `imageio-ffmpeg`.
- VLC and `python-vlc` are optional and used for audio during video preview.
- `tkinterdnd2` is optional and enables drag and drop.

### Python dependencies

```powershell
py -m pip install --upgrade pip
py -m pip install pillow numpy opencv-python imageio imageio-ffmpeg
```

Optional features:

```powershell
py -m pip install python-vlc tkinterdnd2
```

## Installation and launch

1. Install Python 3.10 or newer.
2. Install the required packages listed above.
3. Place `ASCII_STUDIO_PRO_FAST.py` in the project folder.
4. Open PowerShell or Command Prompt in that folder and run:

```powershell
py ASCII_STUDIO_PRO_FAST.py
```

## Quick start

1. Select a file with **Choose file** in the left panel, or drag a file onto the preview area on the right.
2. Set the ASCII resolution and choose a character set.
3. Optionally enter a custom character sequence from light to dark and click **Add**.
4. Select Colour, Monochrome, or Negative appearance.
5. Click **Convert**. Click **Cancel** to stop an active conversion.
6. When conversion finishes, click **Save** to export the result.
7. Click **TR | EN** in the header to switch the interface language.

## Character sets and custom ramps

The application provides built-in ASCII and symbol-based ramps. A custom ramp must contain at least two visible characters. Character order matters: arrange the sequence from light tones to dark tones. Repeated characters and spaces can affect the visual density of the ramp.

## Preview and audio

- GIF previews are animated.
- Video controls provide play/pause, stop, and timeline seeking.
- VLC may be required for audio during video preview.
- Without VLC, video preview may still work but audio preview may be unavailable.

## Conversion process

The source image is sampled into a smaller brightness grid. Each cell's brightness is mapped to a character in the selected ramp. Colour mode uses colours sampled from the source image; monochrome mode uses grayscale values. Negative mode inverts source brightness.

## Troubleshooting

- **Tkinter is missing:** Repair or reinstall Python with Tcl/Tk components enabled.
- **Drag and drop does not work:** Install the optional package with `py -m pip install tkinterdnd2`.
- **No video preview audio:** Check that VLC Media Player and `python-vlc` are installed.
- **A symbol is missing:** Make sure the operating system has a font that supports the symbol.
- **A video cannot be opened:** Check that the file is valid and that its format is supported by OpenCV.

## Project files

```text
ASCII-Studio-Pro/
├── ASCII_STUDIO_PRO_FAST.py
├── README_ASCII_STUDIO_PRO.md
└── LICENSE
```

## License

This project is intended to be released under the **MIT License**. Include a file named `LICENSE` in the project root containing the full MIT License text. Fill in the correct copyright holder and year in that file.

The MIT License permits use, copying, modification, merging, publishing, distribution, sublicensing, and sale of the software, provided that the copyright and permission notices are included in all copies or substantial portions of the software. The software is provided "as is", without warranty of any kind.
