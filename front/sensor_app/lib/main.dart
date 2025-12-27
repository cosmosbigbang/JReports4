import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '계측보고서 자동화',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const SensorForm(),
    );
  }
}

class SensorForm extends StatefulWidget {
  const SensorForm({super.key});

  @override
  State<SensorForm> createState() => _SensorFormState();
}

class _SensorFormState extends State<SensorForm> {
  final _formKey = GlobalKey<FormState>();
  final _siteNameController = TextEditingController();
  final _companyController = TextEditingController();
  final _tController = TextEditingController();
  final _cController = TextEditingController();
  final _seController = TextEditingController();
  final _sController = TextEditingController();
  final _wController = TextEditingController();
  final _iController = TextEditingController();
  
  static const String serverUrl = 'https://jreports4.onrender.com';

  bool _isLoading = false;
  String _resultMessage = '';

  String extractAddress(String siteName) {
    final patterns = [
      RegExp(r'([가-힣]+동)\s*(\d+[-\d]*)'),
      RegExp(r'([가-힣]+리)\s*(\d+[-\d]*)'),
      RegExp(r'([가-힣]+가)\s*(\d+[-\d]*)'),
    ];

    for (var pattern in patterns) {
      final match = pattern.firstMatch(siteName);
      if (match != null) {
        return '${match.group(1)}_${match.group(2)}';
      }
    }

    return siteName.replaceAll(' ', '_');
  }

  Future<void> _generateExcel() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
      _resultMessage = '';
    });

    try {
      final siteName = _siteNameController.text;
      final siteAddress = extractAddress(siteName);

      final response = await http.post(
        Uri.parse('$serverUrl/api/generate-excel/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'site_name': siteName,
          'site_address': siteAddress,
          'company': _companyController.text,
          'counts': {
            'T': int.tryParse(_tController.text) ?? 0,
            'C': int.tryParse(_cController.text) ?? 0,
            'SE': int.tryParse(_seController.text) ?? 0,
            'S': int.tryParse(_sController.text) ?? 0,
            'W': int.tryParse(_wController.text) ?? 0,
            'I': int.tryParse(_iController.text) ?? 0,
          },
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final files = data['files'] as List;
        
        // 저장소 권한 요청
        var status = await Permission.storage.request();
        if (!status.isGranted) {
          status = await Permission.manageExternalStorage.request();
        }
        
        // 다운로드 폴더 경로 가져오기
        Directory? downloadsDir;
        if (Platform.isAndroid) {
          downloadsDir = Directory('/storage/emulated/0/Download/$siteAddress');
        } else {
          downloadsDir = await getApplicationDocumentsDirectory();
        }
        
        if (!await downloadsDir.exists()) {
          await downloadsDir.create(recursive: true);
        }
        
        // 각 파일 저장
        int savedCount = 0;
        for (var file in files) {
          final filename = file['filename'] as String;
          final base64Data = file['data'] as String;
          final bytes = base64Decode(base64Data);
          
          final filePath = '${downloadsDir.path}/$filename';
          final fileObj = File(filePath);
          await fileObj.writeAsBytes(bytes);
          savedCount++;
        }
        
        setState(() {
          _resultMessage = '✅ 생성 완료!\n저장 위치: ${downloadsDir?.path ?? "알 수 없음"}\n파일: $savedCount개\n시간: ${data['elapsed_time']}초';
        });
      } else {
        setState(() {
          _resultMessage = '❌ 오류 발생: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _resultMessage = '❌ 연결 오류: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('계측보고서 자동화'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.blue.shade50,
              Colors.purple.shade50,
            ],
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Container(
              constraints: const BoxConstraints(maxWidth: 600),
              padding: const EdgeInsets.all(32),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text(
                      '계측보고서 엑셀 파일 생성',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),
                    TextFormField(
                      controller: _siteNameController,
                      decoration: const InputDecoration(
                        labelText: '현장명',
                        border: OutlineInputBorder(),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '현장명을 입력하세요';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _companyController,
                      decoration: const InputDecoration(
                        labelText: '계측관리업체',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      '센서 개수',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildNumberField('건물경사계 (T)', _tController),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildNumberField('균열측정계 (C)', _cController),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildNumberField('지표침하계 (SE)', _seController),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildNumberField('변형률계 (S)', _sController),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildNumberField('지하수위계 (W)', _wController),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildNumberField('지중경사계 (I)', _iController),
                        ),
                      ],
                    ),
                    const SizedBox(height: 32),
                    ElevatedButton(
                      onPressed: _isLoading ? null : _generateExcel,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: Colors.blue.shade600,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Text(
                              '엑셀 파일 생성',
                              style: TextStyle(fontSize: 16),
                            ),
                    ),
                    if (_resultMessage.isNotEmpty) ...[
                      const SizedBox(height: 24),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: _resultMessage.contains('✅')
                              ? Colors.green.shade50
                              : Colors.red.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: _resultMessage.contains('✅')
                                ? Colors.green.shade200
                                : Colors.red.shade200,
                          ),
                        ),
                        child: Text(
                          _resultMessage,
                          style: TextStyle(
                            color: _resultMessage.contains('✅')
                                ? Colors.green.shade900
                                : Colors.red.shade900,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNumberField(String label, TextEditingController controller) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
      ),
      keyboardType: TextInputType.number,
      validator: (value) {
        if (value == null || value.isEmpty) {
          return '0 이상';
        }
        final num = int.tryParse(value);
        if (num == null || num < 0) {
          return '0 이상';
        }
        return null;
      },
    );
  }

  @override
  void dispose() {
    _siteNameController.dispose();
    _companyController.dispose();
    _tController.dispose();
    _cController.dispose();
    _seController.dispose();
    _sController.dispose();
    _wController.dispose();
    _iController.dispose();
    super.dispose();
  }
}
