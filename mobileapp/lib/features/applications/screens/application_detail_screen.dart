import 'package:flutter/material.dart';

class ApplicationDetailScreen extends StatelessWidget {
  const ApplicationDetailScreen({required this.applicationId, super.key});

  final String applicationId;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Application Detail')),
      body: Center(
        child: Text('Application $applicationId — Phase 6 implementation'),
      ),
    );
  }
}
