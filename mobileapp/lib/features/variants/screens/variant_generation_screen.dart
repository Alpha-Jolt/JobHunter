import 'package:flutter/material.dart';

class VariantGenerationScreen extends StatelessWidget {
  const VariantGenerationScreen({required this.jobId, super.key});

  final String jobId;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Generate Variant')),
      body: Center(child: Text('Generate for Job $jobId — Phase 5 implementation')),
    );
  }
}
