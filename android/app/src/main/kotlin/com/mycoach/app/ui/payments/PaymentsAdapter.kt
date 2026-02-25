package com.mycoach.app.ui.payments

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.mycoach.app.databinding.ItemPaymentBinding
import com.mycoach.app.models.Payment
import java.text.NumberFormat
import java.util.Locale

class PaymentsAdapter(
    private val onDelete: (Payment) -> Unit
) : ListAdapter<Payment, PaymentsAdapter.ViewHolder>(DIFF) {

    private val euroFmt = NumberFormat.getCurrencyInstance(Locale.FRANCE)

    inner class ViewHolder(private val b: ItemPaymentBinding) : RecyclerView.ViewHolder(b.root) {
        fun bind(p: Payment) {
            b.tvClientName.text = p.clientName
            b.tvDate.text       = p.date
            b.tvAmount.text     = euroFmt.format(p.amount)
            b.tvMethod.text     = p.method ?: ""
            b.root.setOnLongClickListener { onDelete(p); true }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ViewHolder(ItemPaymentBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun onBindViewHolder(holder: ViewHolder, position: Int) = holder.bind(getItem(position))

    companion object {
        val DIFF = object : DiffUtil.ItemCallback<Payment>() {
            override fun areItemsTheSame(a: Payment, b: Payment) = a.id == b.id
            override fun areContentsTheSame(a: Payment, b: Payment) = a == b
        }
    }
}
