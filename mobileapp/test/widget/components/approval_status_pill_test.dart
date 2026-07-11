import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jobhunter/shared/components/approval_status_pill.dart';

void main() {
  Widget wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

  group('ApprovalStatusPill', () {
    testWidgets('shows Pending Review for pending status', (tester) async {
      await tester.pumpWidget(
        wrap(const ApprovalStatusPill(status: ApprovalStatus.pending)),
      );
      expect(find.text('Pending Review'), findsOneWidget);
    });

    testWidgets('shows Approved for approved status', (tester) async {
      await tester.pumpWidget(
        wrap(const ApprovalStatusPill(status: ApprovalStatus.approved)),
      );
      expect(find.text('Approved'), findsOneWidget);
    });

    testWidgets('shows Rejected for rejected status', (tester) async {
      await tester.pumpWidget(
        wrap(const ApprovalStatusPill(status: ApprovalStatus.rejected)),
      );
      expect(find.text('Rejected'), findsOneWidget);
    });

    testWidgets('shows Expired for expired status', (tester) async {
      await tester.pumpWidget(
        wrap(const ApprovalStatusPill(status: ApprovalStatus.expired)),
      );
      expect(find.text('Expired'), findsOneWidget);
    });
  });

  group('parseApprovalStatus', () {
    test('approved string maps to approved', () {
      expect(parseApprovalStatus('approved'), ApprovalStatus.approved);
    });

    test('rejected string maps to rejected', () {
      expect(parseApprovalStatus('rejected'), ApprovalStatus.rejected);
    });

    test('null maps to pending', () {
      expect(parseApprovalStatus(null), ApprovalStatus.pending);
    });

    test('tokenExpired=true overrides status to expired', () {
      expect(
        parseApprovalStatus('approved', tokenExpired: true),
        ApprovalStatus.expired,
      );
    });
  });
}
