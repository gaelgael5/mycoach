package com.mycoach.app.ui.clients

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.mycoach.app.R
import com.mycoach.app.databinding.ItemClientBinding
import com.mycoach.app.models.Client
import java.text.NumberFormat
import java.util.Locale

class ClientsAdapter(
    private val onEdit: (Client) -> Unit,
    private val onDelete: (Client) -> Unit,
) : ListAdapter<Client, ClientsAdapter.ViewHolder>(DIFF) {

    private val euroFmt = NumberFormat.getCurrencyInstance(Locale.FRANCE)

    inner class ViewHolder(private val b: ItemClientBinding) : RecyclerView.ViewHolder(b.root) {
        fun bind(client: Client) {
            b.tvName.text    = client.name
            b.tvEmail.text   = client.email ?: client.phone ?: ""
            b.tvHours.text   = "${client.totalHours}h · ${euroFmt.format(client.hourlyRate)}/h"
            b.tvBalance.text = euroFmt.format(client.balance)
            b.tvBalance.setTextColor(
                ContextCompat.getColor(b.root.context, if (client.balance > 0) R.color.red else R.color.green)
            )
            b.root.setOnClickListener { onEdit(client) }
            b.root.setOnLongClickListener { onDelete(client); true }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ViewHolder(ItemClientBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun onBindViewHolder(holder: ViewHolder, position: Int) = holder.bind(getItem(position))

    companion object {
        val DIFF = object : DiffUtil.ItemCallback<Client>() {
            override fun areItemsTheSame(a: Client, b: Client) = a.id == b.id
            override fun areContentsTheSame(a: Client, b: Client) = a == b
        }
    }
}
