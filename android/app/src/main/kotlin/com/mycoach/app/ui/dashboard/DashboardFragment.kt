package com.mycoach.app.ui.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.mycoach.app.databinding.FragmentDashboardBinding
import java.text.NumberFormat
import java.util.Locale

class DashboardFragment : Fragment() {

    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DashboardViewModel by viewModels()
    private val euroFmt = NumberFormat.getCurrencyInstance(Locale.FRANCE)

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.loading.observe(viewLifecycleOwner) {
            binding.progressBar.visibility = if (it) View.VISIBLE else View.GONE
        }

        viewModel.error.observe(viewLifecycleOwner) { err ->
            binding.tvError.visibility = if (err != null) View.VISIBLE else View.GONE
            binding.tvError.text = err
        }

        viewModel.stats.observe(viewLifecycleOwner) { stats ->
            binding.tvClients.text     = stats.totalClients.toString()
            binding.tvSessions.text    = stats.totalSessions.toString()
            binding.tvHours.text       = "${stats.totalHours}h"
            binding.tvRevenue.text     = euroFmt.format(stats.totalRevenue)
            binding.tvPaid.text        = euroFmt.format(stats.totalPaid)
            binding.tvOutstanding.text = euroFmt.format(stats.totalOutstanding)
        }

        viewModel.load()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
