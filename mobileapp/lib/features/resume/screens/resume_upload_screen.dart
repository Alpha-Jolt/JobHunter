import 'package:flutter/material.dart';

class ResumeUploadScreen extends StatelessWidget {
  const ResumeUploadScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload Resume')),
      body: const Center(
        child: Text('Resume Upload — Phase 4 implementation'),
      ),
    );
  }
}
