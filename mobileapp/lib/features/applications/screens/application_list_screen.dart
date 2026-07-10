import 'package:flutter/material.dart';

class ApplicationListScreen extends StatelessWidget {
  const ApplicationListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Applications')),
      body: const Center(child: Text('Applications — Phase 6 implementation')),
    );
  }
}
