import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';
import '../../core/theme/app_colors.dart';

class ShimmerList extends StatelessWidget {
  final int itemCount;
  const ShimmerList({super.key, this.itemCount = 6});

  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Colors.grey.shade300,
      highlightColor: Colors.grey.shade100,
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: itemCount,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (_, __) => Card(
          child: ListTile(
            leading: const CircleAvatar(backgroundColor: Colors.white),
            title: Container(height: 14, width: 120, color: Colors.white),
            subtitle: Container(height: 10, width: 80, color: Colors.white),
          ),
        ),
      ),
    );
  }
}
