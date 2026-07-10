import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jobhunter/shared/components/gap_tag_chip.dart';

void main() {
  Widget _wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

  group('GapTagChip — no-fabrication guarantee', () {
    testWidgets('always contains "not in your resume" label text',
        (tester) async {
      // Arrange + Act
      await tester.pumpWidget(_wrap(const GapTagChip(gap: 'Kubernetes')));

      // Assert — gap must NEVER be presented as a present skill
      final text = tester.widget<Text>(find.byType(Text).last);
      expect(
        text.data?.toLowerCase(),
        contains('not in your resume'),
      );
    });

    testWidgets('displays the gap skill name', (tester) async {
      // Arrange + Act
      await tester.pumpWidget(_wrap(const GapTagChip(gap: 'Docker')));

      // Assert
      expect(find.textContaining('Docker'), findsOneWidget);
    });

    testWidgets('never shows a green check icon (must not imply skill present)',
        (tester) async {
      // Arrange + Act
      await tester.pumpWidget(_wrap(const GapTagChip(gap: 'Python')));

      // Assert — no check icons that could imply skill is present
      expect(find.byIcon(Icons.check), findsNothing);
      expect(find.byIcon(Icons.check_circle), findsNothing);
      expect(find.byIcon(Icons.check_circle_outline), findsNothing);
    });
  });
}
