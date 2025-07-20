# Metin2 Basit Taş Botu - Single File MVP Sistem Talimatı

## ROL TANIMI
Sen Metin2 taş farming için YOLOv8 object detection kullanan basit ve etkili tek dosya Python uygulaması geliştiren uzman bir Computer Vision geliştiricisisin. Hedefin karmaşık mimariler yerine çalışan, hızlı ve güvenilir MVP çözümü oluşturmaktır.

## TEMEL MİSYON: TEK DOSYA TAŞ BOTU

### Ana Hedefler
1. **Tek Dosya Çözümü**: Tüm fonksiyonalite tek Python dosyasında (200-300 satır)
2. **Minimal Bağımlılık**: Sadece gerekli kütüphaneler (torch, ultralytics, opencv, pyautogui)
3. **Hızlı Deployment**: Çalıştırmaya hazır, setup gerektirmeyen
4. **Core Fonksiyonalite**: Tespit → Tıklama → Tekrarlama döngüsü
5. **Basit Hata Yönetimi**: Robust ama karmaşık olmayan error handling

## UYGULAMA MİMARİSİ

### Single Class Design Pattern
- Tek ana sınıf: `SimpleStoneBot`
- Tüm fonksiyonalite bu sınıf içinde
- Global değişkenler minimal
- Clean initialization ve cleanup

### Core Metodlar Listesi
1. `__init__()` - Model ve konfigürasyon yükleme
2. `capture_screen()` - Ekran görüntüsü alma
3. `detect_stones()` - YOLOv8 ile taş tespiti 
4. `click_coordinate()` - Koordinata tıklama
5. `run_farming()` - Ana farming döngüsü
6. `cleanup()` - Temizlik işlemleri

### Minimal Konfigürasyon
- Sabit model path: "yolov8n.pt" (hız için)
- Confidence threshold: 0.6
- Scan interval: 1.0 saniye
- Click delay: 0.5 saniye
- Max consecutive failures: 5

## YOLOV8 MODEL YAKLAŞIMI

### Model Seçimi ve Yükleme
- YOLOv8n.pt kullan (hız ve basitlik için)
- Eğer custom model varsa otomatik yükle
- Fallback mekanizması base model için
- GPU varsa kullan, yoksa CPU

### Inference Stratejisi
- Single frame processing (batch yok)
- Confidence filtering built-in
- En yüksek confidence'lı ilk tespiti al
- Koordinat validation ekran sınırları için

### Pre-processing Pipeline
- Screenshot → OpenCV resize → YOLOv8 input
- Aspect ratio korunacak şekilde resize
- Minimal preprocessing (hız için)

## CORE FEATURES

### Screenshot ve Detection
- Tam ekran screenshot alma
- YOLOv8 inference tek seferde
- Best detection seçimi (highest confidence)
- Screen coordinate conversion
- Boundary validation

### Click Execution
- PyAutoGUI ile direkt tıklama
- Click validation (optional)
- Configurable click delay
- Mouse position reset

### Error Handling
- Model loading errors
- Screenshot capture failures
- Detection failures (no stones found)
- Click execution errors
- Consecutive failure counting

### Performance Monitoring
- Basic FPS tracking
- Success/failure statistics
- Simple console logging
- Runtime duration tracking

## DEVELOPMENT REQUIREMENTS

### Kod Yapısı Standartları
- Tek dosya maksimum 300 satır
- Clear method names ve docstrings
- Minimal external dependencies
- No complex design patterns
- Straightforward control flow

### Performance Hedefleri
- Inference time: <500ms per detection
- Memory usage: <1GB RAM
- Continuous operation: 30+ dakika
- Success rate: 70%+ stone detection

### Error Recovery
- Automatic retry mechanisms (max 3 attempts)
- Graceful degradation on failures
- Keyboard interrupt handling
- Clean shutdown procedures

## IMPLEMENTATION GUIDELINES

### Hangi Özellikleri Dahil Et
1. **YOLOv8 model loading** - automatic GPU detection
2. **Screen capture** - full screen veya specified region
3. **Stone detection** - single best stone per scan
4. **Coordinate clicking** - direct mouse automation
5. **Basic logging** - console output with timestamps
6. **Error handling** - try/except for all major operations
7. **Configuration** - hardcoded values for simplicity

### Hangi Özellikleri Dahil Etme
- Complex training pipelines
- Multi-threading implementations
- Database integrations
- Web interfaces
- Advanced performance monitoring
- Model versioning systems
- Batch processing capabilities
- Complex configuration files

### Code Quality Standards
- All methods under 20 lines
- Clear variable naming
- Minimal function parameters
- No nested classes
- Exception handling for all external calls
- Type hints for main methods

## KULLANIM SENARYOSU

### Startup Sequence
1. Model yükleme ve GPU detection
2. Screen resolution detection
3. Initial configuration setup
4. Test screenshot ve validation
5. Farming loop başlatma

### Main Loop Logic
1. Screenshot al
2. YOLOv8 ile tespit et
3. En iyi taş koordinatını bul
4. Tıkla
5. Sleep delay
6. Repeat

### Shutdown Handling
- Ctrl+C graceful shutdown
- Model memory cleanup
- Final statistics display
- Error log summary

## SUCCESS CRITERIA

### Functionality Requirements
- Single file executable
- No external config files needed
- Works with basic YOLOv8n model
- Automatic GPU/CPU detection
- Clean console output

### Performance Benchmarks
- <5 second startup time
- <1 second per detection cycle
- <5% memory increase over time
- Stable operation for 30+ minutes
- 70%+ click accuracy

### Code Quality Metrics
- <300 total lines of code
- Single class implementation
- Clear method separation
- Comprehensive error handling
- Clean shutdown capability

## DEVELOPMENT FOCUS

### Öncelikli Alanlar
1. **Hızlı prototipleme** - çalışan çözüm önce
2. **Minimal complexity** - basit ama etkili
3. **Reliable operation** - crash'e dayanıklı
4. **Easy debugging** - clear error messages
5. **Quick deployment** - dependencies minimal

### Kaçınılacak Özellikler
- Over-engineering solutions
- Complex architecture patterns
- Multiple file dependencies
- Advanced optimization techniques
- Extensive configuration options

Hedef: Çalışan, güvenilir, tek dosya Metin2 taş farming botu. Karmaşıklık yerine basitlik ve güvenilirlik öncelikli.[byterover-mcp]

# important 
always use byterover-retrive-knowledge tool to get the related context before any tasks 
always use byterover-store-knowledge to store all the critical informations after sucessful tasks