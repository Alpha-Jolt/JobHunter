import 'package:flutter/material.dart';

/// Simple horizontal or vertical divider using theme colors.
class AppDivider extends StatelessWidget {
  const AppDivider({
    this.vertical = false,
    this.indent = 0.0,
    this.endIndent = 0.0,
    super.key,
  });

  final bool vertical;
  final double indent;
  final double endIndent;

  @override
  Widget build(BuildContext context) {
    if (vertical) {
      return VerticalDivider(
        width: 1,
        thickness: 1,
        color: Theme.of(context).colorScheme.outlineVariant,
        indent: indent,
        endIndent: endIndent,
      );
    }
    return Divider(
      height: 1,
      thickness: 1,
      color: Theme.of(context).colorScheme.outlineVariant,
      indent: indent,
      endIndent: endIndent,
    );
  }
}
