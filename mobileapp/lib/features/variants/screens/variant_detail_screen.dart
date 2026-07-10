import 'package:flutter/material.dart';

class VariantDetailScreen extends StatelessWidget {
  const VariantDetailScreen({required this.variantId, super.key});

  final String variantId;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Variant Detail')),
      body: Center(child: Text('Variant $variantId — Phase 5 implementation')),
    );
  }
}
