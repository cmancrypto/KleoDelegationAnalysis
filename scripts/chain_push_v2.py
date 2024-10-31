import pandas as pd
import json
from get_chain_revenues import get_delegator_list


def get_delegator_allocations(chain_name: str, snapshot_date: str, allocation_multiplier: float = 0.383):
    """
    Get delegator list and calculate allocations based on staked amounts.

    Args:
        chain_name: Name of the chain
        snapshot_date: Date in yyyy-mm-dd format
        allocation_multiplier: Multiplier to calculate allocation amount (default 0.383)

    Returns:
        DataFrame with delegator addresses and allocations
    """
    # Get delegator data from snapshot
    data = get_delegator_list(chain_name, snapshot_date)
    if not data:
        raise ValueError(f"Could not get delegator data for {chain_name} on {snapshot_date}")

    # Convert delegators list to DataFrame
    delegators = data["delegators"]
    df = pd.DataFrame(delegators)
    # Rename columns for clarity
    df = df.rename(columns={
        "address": "address",
        "amount": "snapshot_amount"
    })

    # Calculate allocation amount
    df["amount"] = df["snapshot_amount"] * allocation_multiplier

    # Select and order required columns
    result_df = df[["address", "amount"]]

    return result_df


def save_allocations_to_json(df: pd.DataFrame, output_file: str = "delegator_allocations.json"):
    """
    Save the allocations DataFrame to a JSON file

    Args:
        df: DataFrame containing allocations
        output_file: Name of output JSON file
    """
    # Convert DataFrame to records format and save to JSON
    allocations = df.to_dict(orient="records")
    with open(output_file, "w") as f:
        json.dump(allocations, f, indent=2)


def main(chain_name: str, snapshot_date: str, allocation_multiplier : float, output_file: str = "delegator_allocations.json"):
    """
    Main function to get delegator allocations and save to JSON

    Args:
        chain_name: Name of the chain
        snapshot_date: Date in yyyy-mm-dd format
        output_file: Name of output JSON file
    """
    try:
        # Get allocations DataFrame
        df = get_delegator_allocations(chain_name, snapshot_date)

        # Save to JSON
        save_allocations_to_json(df, output_file)

        print(f"Successfully saved allocations to {output_file}")
        print(f"Total delegators: {len(df)}")
        print(f"Total allocation amount: {df['amount'].sum():.2f}")

    except Exception as e:
        print(f"Error processing delegator allocations: {str(e)}")
        raise


if __name__ == "__main__":
    chain_name = "osmosis"
    snapshot_date = "2024-10-30"
    allocation_multiplier = 0.3833
    main(chain_name, snapshot_date, allocation_multiplier)