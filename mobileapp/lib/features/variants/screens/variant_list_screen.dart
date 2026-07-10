import 'package:flutter/material.dart';

class VariantListScreen extends StatelessWidget {
  const VariantListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Variants')),
      body: const Center(child: Text('Variant List — Phase 5 implementation')),
    );
  }
}
