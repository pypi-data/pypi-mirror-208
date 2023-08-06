/** Copyright 2022 Alibaba Group Holding Limited.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#ifndef GAR_GRAPH_H_
#define GAR_GRAPH_H_

#include <any>
#include <limits>
#include <map>
#include <memory>
#include <string>
#include <utility>
#include <variant>
#include <vector>

#include "gar/reader/arrow_chunk_reader.h"
#include "gar/utils/reader_utils.h"
#include "gar/utils/utils.h"

// forward declarations
namespace arrow {
class ChunkedArray;
}

namespace GAR_NAMESPACE_INTERNAL {

/**
 * @brief Vertex contains information of certain vertex.
 */
class Vertex {
 public:
  /**
   * Initialize the Vertex.
   *
   * @param id The vertex id.
   * @param readers A set of readers for reading the vertex properties.
   */
  explicit Vertex(
      IdType id,
      std::vector<VertexPropertyArrowChunkReader>& readers);  // NOLINT

  /**
   * @brief Get the id of the vertex.
   *
   * @return The id of the vertex.
   */
  inline IdType id() const noexcept { return id_; }

  /**
   * @brief Get the property value of the vertex.
   *
   * @param property The property name.
   * @return Result: The property value or error.
   */
  template <typename T>
  inline Result<T> property(const std::string& property) noexcept {
    T ret;
    if (properties_.find(property) == properties_.end()) {
      return Status::KeyError("The property is not exist.");
    }
    try {
      ret = std::any_cast<T>(properties_[property]);
    } catch (const std::bad_any_cast& e) {
      return Status::TypeError("The property type is not match.");
    }
    return ret;
  }

 private:
  IdType id_;
  std::map<std::string, std::any> properties_;
};

/**
 * @brief Edge contains information of certain edge.
 */
class Edge {
 public:
  /**
   * Initialize the Edge.
   *
   * @param adj_list_reader The reader for reading the adjList.
   * @param property_readers A set of readers for reading the edge properties.
   */
  explicit Edge(AdjListArrowChunkReader& adj_list_reader,  // NOLINT
                std::vector<AdjListPropertyArrowChunkReader>&
                    property_readers);  // NOLINT

  /**
   * @brief Get source id of the edge.
   *
   * @return The id of the source vertex.
   */
  inline IdType source() const noexcept { return src_id_; }

  /**
   * @brief Get destination id of the edge.
   *
   * @return The id of the destination vertex.
   */
  inline IdType destination() const noexcept { return dst_id_; }

  /**
   * @brief Get the property value of the edge.
   *
   * @param property The property name.
   * @return Result: The property value or error.
   */
  template <typename T>
  inline Result<T> property(const std::string& property) noexcept {
    T ret;
    if (properties_.find(property) == properties_.end()) {
      return Status::KeyError("The property is not exist.");
    }
    try {
      ret = std::any_cast<T>(properties_[property]);
    } catch (const std::bad_any_cast& e) {
      return Status::TypeError("The property type is not match.");
    }
    return ret;
  }

 private:
  IdType src_id_, dst_id_;
  std::map<std::string, std::any> properties_;
};

/**
 * @brief The iterator for traversing a type of vertices.
 *
 */
class VertexIter {
 public:
  /**
   * Initialize the iterator.
   *
   * @param vertex_info The vertex info that describes the vertex type.
   * @param prefix The absolute prefix.
   * @param offset The current offset of the readers.
   */
  explicit VertexIter(const VertexInfo& vertex_info, const std::string& prefix,
                      IdType offset) noexcept {
    for (const auto& pg : vertex_info.GetPropertyGroups()) {
      readers_.emplace_back(vertex_info, pg, prefix);
    }
    cur_offset_ = offset;
  }

  /** Copy constructor. */
  VertexIter(const VertexIter& other)
      : readers_(other.readers_), cur_offset_(other.cur_offset_) {}

  /** Construct and return the vertex of the current offset. */
  Vertex operator*() noexcept {
    for (auto& reader : readers_) {
      reader.seek(cur_offset_);
    }
    return Vertex(cur_offset_, readers_);
  }

  /** Get the vertex id of the current offset. */
  IdType id() { return cur_offset_; }

  /** Get the value for a property of the current vertex. */
  template <typename T>
  Result<T> property(const std::string& property) noexcept {
    std::shared_ptr<arrow::ChunkedArray> column(nullptr);
    for (auto& reader : readers_) {
      reader.seek(cur_offset_);
      GAR_ASSIGN_OR_RAISE(auto chunk_table, reader.GetChunk());
      column = util::GetArrowColumnByName(chunk_table, property);
      if (column != nullptr) {
        break;
      }
    }
    if (column != nullptr) {
      auto array = util::GetArrowArrayByChunkIndex(column, 0);
      GAR_ASSIGN_OR_RAISE(auto data, util::GetArrowArrayData(array));
      return util::ValueGetter<T>::Value(data, 0);
    }
    return Status::KeyError("The property is not exist.");
  }

  /** The prefix increment operator. */
  VertexIter& operator++() noexcept {
    ++cur_offset_;
    return *this;
  }

  /** The postfix increment operator. */
  VertexIter operator++(int) {
    VertexIter ret(*this);
    ++cur_offset_;
    return ret;
  }

  /** The add operator. */
  VertexIter operator+(IdType offset) {
    VertexIter ret(*this);
    ret.cur_offset_ += offset;
    return ret;
  }

  /** The equality operator. */
  bool operator==(const VertexIter& rhs) const noexcept {
    return cur_offset_ == rhs.cur_offset_;
  }

  /** The inequality operator. */
  bool operator!=(const VertexIter& rhs) const noexcept {
    return cur_offset_ != rhs.cur_offset_;
  }

 private:
  std::vector<VertexPropertyArrowChunkReader> readers_;
  IdType cur_offset_;
};

/**
 * @brief VerticesCollection is designed for reading a collection of vertices.
 *
 */
class VerticesCollection {
 public:
  /**
   * @brief Initialize the VerticesCollection.
   *
   * @param vertex_info The vertex info that describes the vertex type.
   * @param prefix The absolute prefix.
   */
  explicit VerticesCollection(const VertexInfo& vertex_info,
                              const std::string& prefix)
      : vertex_info_(vertex_info), prefix_(prefix) {
    // get the vertex num
    std::string base_dir;
    GAR_ASSIGN_OR_RAISE_ERROR(auto fs,
                              FileSystemFromUriOrPath(prefix, &base_dir));
    GAR_ASSIGN_OR_RAISE_ERROR(auto file_path,
                              vertex_info.GetVerticesNumFilePath());
    std::string vertex_num_path = base_dir + file_path;
    GAR_ASSIGN_OR_RAISE_ERROR(vertex_num_,
                              fs->ReadFileToValue<IdType>(vertex_num_path));
  }

  /** The iterator pointing to the first vertex. */
  VertexIter begin() noexcept { return VertexIter(vertex_info_, prefix_, 0); }

  /** The iterator pointing to the past-the-end element. */
  VertexIter end() noexcept {
    return VertexIter(vertex_info_, prefix_, vertex_num_);
  }

  /** The iterator pointing to the vertex with specific id. */
  VertexIter find(IdType id) { return VertexIter(vertex_info_, prefix_, id); }

  /** Get the number of vertices in the collection. */
  size_t size() const noexcept { return vertex_num_; }

 private:
  VertexInfo vertex_info_;
  std::string prefix_;
  IdType vertex_num_;
};

/**
 * @brief EdgesCollection is designed for reading a collection of edges.
 *
 */
template <AdjListType adj_list_type>
class EdgesCollection;

/**
 * @brief The iterator for traversing a type of edges.
 *
 */
class EdgeIter {
 public:
  /**
   * Initialize the iterator.
   *
   * @param edge_info The edge info that describes the edge type.
   * @param prefix The absolute prefix.
   * @param adj_list_type The type of adjList.
   * @param global_chunk_index The global index of the current edge chunk.
   * @param offset The current offset in the current edge chunk.
   * @param chunk_begin The index of the first chunk.
   * @param chunk_end The index of the last chunk.
   * @param index_converter The converter for transforming the edge chunk
   * indices.
   */
  explicit EdgeIter(const EdgeInfo& edge_info, const std::string& prefix,
                    AdjListType adj_list_type, IdType global_chunk_index,
                    IdType offset, IdType chunk_begin, IdType chunk_end,
                    std::shared_ptr<util::IndexConverter> index_converter)
      : adj_list_reader_(
            edge_info, adj_list_type, prefix,
            index_converter->GlobalChunkIndexToIndexPair(global_chunk_index)
                .first),
        global_chunk_index_(global_chunk_index),
        cur_offset_(offset),
        chunk_size_(edge_info.GetChunkSize()),
        src_chunk_size_(edge_info.GetSrcChunkSize()),
        dst_chunk_size_(edge_info.GetDstChunkSize()),
        num_row_of_chunk_(0),
        chunk_begin_(chunk_begin),
        chunk_end_(chunk_end),
        adj_list_type_(adj_list_type),
        index_converter_(index_converter) {
    vertex_chunk_index_ =
        index_converter->GlobalChunkIndexToIndexPair(global_chunk_index).first;
    GAR_ASSIGN_OR_RAISE_ERROR(auto& property_groups,
                              edge_info.GetPropertyGroups(adj_list_type));
    for (const auto& pg : property_groups) {
      property_readers_.emplace_back(edge_info, pg, adj_list_type, prefix,
                                     vertex_chunk_index_);
    }
    if (adj_list_type == AdjListType::ordered_by_source ||
        adj_list_type == AdjListType::ordered_by_dest) {
      offset_reader_ = std::make_shared<AdjListOffsetArrowChunkReader>(
          edge_info, adj_list_type, prefix);
    }
  }

  /** Copy constructor. */
  EdgeIter(const EdgeIter& other)
      : adj_list_reader_(other.adj_list_reader_),
        offset_reader_(other.offset_reader_),
        property_readers_(other.property_readers_),
        global_chunk_index_(other.global_chunk_index_),
        vertex_chunk_index_(other.vertex_chunk_index_),
        cur_offset_(other.cur_offset_),
        chunk_size_(other.chunk_size_),
        src_chunk_size_(other.src_chunk_size_),
        dst_chunk_size_(other.dst_chunk_size_),
        num_row_of_chunk_(other.num_row_of_chunk_),
        chunk_begin_(other.chunk_begin_),
        chunk_end_(other.chunk_end_),
        adj_list_type_(other.adj_list_type_),
        index_converter_(other.index_converter_) {}

  /** Construct and return the edge of the current offset. */
  Edge operator*() {
    adj_list_reader_.seek(cur_offset_);
    for (auto& reader : property_readers_) {
      reader.seek(cur_offset_);
    }
    return Edge(adj_list_reader_, property_readers_);
  }

  /** Get the source vertex id for the current edge. */
  IdType source();

  /** Get the destination vertex id for the current edge. */
  IdType destination();

  /** Get the value of a property for the current edge. */
  template <typename T>
  Result<T> property(const std::string& property) noexcept {
    std::shared_ptr<arrow::ChunkedArray> column(nullptr);
    for (auto& reader : property_readers_) {
      reader.seek(cur_offset_);
      GAR_ASSIGN_OR_RAISE(auto chunk_table, reader.GetChunk());
      column = util::GetArrowColumnByName(chunk_table, property);
      if (column != nullptr) {
        break;
      }
    }
    if (column != nullptr) {
      auto array = util::GetArrowArrayByChunkIndex(column, 0);
      GAR_ASSIGN_OR_RAISE(auto data, util::GetArrowArrayData(array));
      return util::ValueGetter<T>::Value(data, 0);
    }
    return Status::KeyError("The property is not exist.");
  }

  /** The prefix increment operator. */
  EdgeIter& operator++() {
    if (num_row_of_chunk_ == 0) {
      adj_list_reader_.seek(cur_offset_);
      GAR_ASSIGN_OR_RAISE_ERROR(num_row_of_chunk_,
                                adj_list_reader_.GetRowNumOfChunk());
    }
    auto st = adj_list_reader_.seek(++cur_offset_);
    if (st.ok() && num_row_of_chunk_ != chunk_size_) {
      // check the row offset is overflow
      auto row_offset = cur_offset_ % chunk_size_;
      if (row_offset >= num_row_of_chunk_) {
        cur_offset_ = (cur_offset_ / chunk_size_ + 1) * chunk_size_;
        adj_list_reader_.seek(cur_offset_);
        st = Status::KeyError();
      }
    }
    if (st.ok() && num_row_of_chunk_ == chunk_size_ &&
        cur_offset_ % chunk_size_ == 0) {
      GAR_ASSIGN_OR_RAISE_ERROR(num_row_of_chunk_,
                                adj_list_reader_.GetRowNumOfChunk());
      ++global_chunk_index_;
    }
    if (st.IsKeyError()) {
      st = adj_list_reader_.next_chunk();
      ++global_chunk_index_;
      ++vertex_chunk_index_;
      if (!st.IsOutOfRange()) {
        GAR_ASSIGN_OR_RAISE_ERROR(num_row_of_chunk_,
                                  adj_list_reader_.GetRowNumOfChunk());
        for (auto& reader : property_readers_) {
          reader.next_chunk();
        }
      }
      cur_offset_ = 0;
      adj_list_reader_.seek(cur_offset_);
    }
    return *this;
  }

  /** The postfix increment operator. */
  EdgeIter operator++(int) {
    EdgeIter ret(*this);
    this->operator++();
    return ret;
  }

  /** The copy assignment operator. */
  EdgeIter operator=(const EdgeIter& other) {
    adj_list_reader_ = other.adj_list_reader_;
    offset_reader_ = other.offset_reader_;
    property_readers_ = other.property_readers_;
    global_chunk_index_ = other.global_chunk_index_;
    vertex_chunk_index_ = other.vertex_chunk_index_;
    cur_offset_ = other.cur_offset_;
    chunk_size_ = other.chunk_size_;
    src_chunk_size_ = other.src_chunk_size_;
    dst_chunk_size_ = other.dst_chunk_size_;
    num_row_of_chunk_ = other.num_row_of_chunk_;
    chunk_begin_ = other.chunk_begin_;
    chunk_end_ = other.chunk_end_;
    adj_list_type_ = other.adj_list_type_;
    index_converter_ = other.index_converter_;
    return *this;
  }

  /** The equality operator. */
  bool operator==(const EdgeIter& rhs) const noexcept {
    return global_chunk_index_ == rhs.global_chunk_index_ &&
           cur_offset_ == rhs.cur_offset_ &&
           adj_list_type_ == rhs.adj_list_type_;
  }

  /** The inequality operator. */
  bool operator!=(const EdgeIter& rhs) const noexcept {
    return global_chunk_index_ != rhs.global_chunk_index_ ||
           cur_offset_ != rhs.cur_offset_ ||
           adj_list_type_ != rhs.adj_list_type_;
  }

  /** Get the global index of the current edge chunk. */
  IdType global_chunk_index() const { return global_chunk_index_; }

  /** Get the current offset in the current chunk. */
  IdType cur_offset() const { return cur_offset_; }

  /**
   * Let the input iterator to point to the first out-going edge of the
   * vertex with specific id after the current position of the iterator.
   *
   * @param from The input iterator.
   * @param id The vertex id.
   * @return If such edge is found or not.
   */
  bool first_src(const EdgeIter& from, IdType id);

  /**
   * Let the input iterator to point to the first incoming edge of the
   * vertex with specific id after the current position of the iterator.
   *
   * @param from The input iterator.
   * @param id The vertex id.
   * @return If such edge is found or not.
   */
  bool first_dst(const EdgeIter& from, IdType id);

  /** Let the iterator to point to the begin. */
  void to_begin() {
    global_chunk_index_ = chunk_begin_;
    cur_offset_ = 0;
    vertex_chunk_index_ =
        index_converter_->GlobalChunkIndexToIndexPair(global_chunk_index_)
            .first;
    refresh();
  }

  /** Check if the current position is the end. */
  bool is_end() const { return global_chunk_index_ >= chunk_end_; }

  /** Point to the next edge with the same source, return false if not found. */
  bool next_src() {
    if (is_end())
      return false;
    IdType id = this->source();
    IdType pre_vertex_chunk_index = vertex_chunk_index_;
    if (adj_list_type_ == AdjListType::ordered_by_source) {
      this->operator++();
      if (is_end() || this->source() != id)
        return false;
      else
        return true;
    }
    this->operator++();
    while (!is_end()) {
      if (this->source() == id) {
        return true;
      }
      if (adj_list_type_ == AdjListType::unordered_by_source) {
        if (vertex_chunk_index_ > pre_vertex_chunk_index)
          return false;
      }
      this->operator++();
    }
    return false;
  }

  /**
   * Point to the next edge with the same destination, return false if not
   * found.
   */
  bool next_dst() {
    if (is_end())
      return false;
    IdType id = this->destination();
    IdType pre_vertex_chunk_index = vertex_chunk_index_;
    if (adj_list_type_ == AdjListType::ordered_by_dest) {
      this->operator++();
      if (is_end() || this->destination() != id)
        return false;
      else
        return true;
    }
    this->operator++();
    while (!is_end()) {
      if (this->destination() == id) {
        return true;
      }
      if (adj_list_type_ == AdjListType::unordered_by_dest) {
        if (vertex_chunk_index_ > pre_vertex_chunk_index)
          return false;
      }
      this->operator++();
    }
    return false;
  }

  /**
   * Point to the next edge with the specific source, return false if not
   * found.
   */
  bool next_src(IdType id) {
    if (is_end())
      return false;
    this->operator++();
    return this->first_src(*this, id);
  }

  /**
   * Point to the next edge with the specific destination, return false if
   * not found.
   */
  bool next_dst(IdType id) {
    if (is_end())
      return false;
    this->operator++();
    return this->first_dst(*this, id);
  }

 private:
  // Refresh the readers to point to the current position.
  void refresh() {
    adj_list_reader_.seek_chunk_index(vertex_chunk_index_);
    adj_list_reader_.seek(cur_offset_);
    for (auto& reader : property_readers_) {
      reader.seek_chunk_index(vertex_chunk_index_);
    }
    GAR_ASSIGN_OR_RAISE_ERROR(num_row_of_chunk_,
                              adj_list_reader_.GetRowNumOfChunk());
  }

 private:
  AdjListArrowChunkReader adj_list_reader_;
  std::shared_ptr<AdjListOffsetArrowChunkReader> offset_reader_;
  std::vector<AdjListPropertyArrowChunkReader> property_readers_;
  IdType global_chunk_index_;
  IdType vertex_chunk_index_;
  IdType cur_offset_;
  IdType chunk_size_;
  IdType src_chunk_size_;
  IdType dst_chunk_size_;
  IdType num_row_of_chunk_;
  IdType chunk_begin_, chunk_end_;
  AdjListType adj_list_type_;
  std::shared_ptr<util::IndexConverter> index_converter_;

  friend class EdgesCollection<AdjListType::ordered_by_source>;
  friend class EdgesCollection<AdjListType::ordered_by_dest>;
  friend class EdgesCollection<AdjListType::unordered_by_source>;
  friend class EdgesCollection<AdjListType::unordered_by_dest>;
};

/**
 * @brief The implementation of EdgesCollection when the type of adjList is
 * AdjListType::ordered_by_source.
 *
 */
template <>
class EdgesCollection<AdjListType::ordered_by_source> {
 public:
  static const AdjListType adj_list_type_;

  /**
   * @brief Initialize the EdgesCollection with a range of chunks.
   *
   * @param edge_info The edge info that describes the edge type.
   * @param prefix The absolute prefix.
   * @param vertex_chunk_begin The index of the begin vertex chunk.
   * @param vertex_chunk_end The index of the end vertex chunk (not included).
   */
  EdgesCollection(const EdgeInfo& edge_info, const std::string& prefix,
                  IdType vertex_chunk_begin = 0,
                  IdType vertex_chunk_end = std::numeric_limits<int64_t>::max())
      : edge_info_(edge_info), prefix_(prefix) {
    GAR_ASSIGN_OR_RAISE_ERROR(
        auto vertex_chunk_num,
        utils::GetVertexChunkNum(prefix_, edge_info_, adj_list_type_));
    std::vector<IdType> edge_chunk_nums(vertex_chunk_num, 0);
    if (vertex_chunk_end == std::numeric_limits<int64_t>::max()) {
      vertex_chunk_end = vertex_chunk_num;
    }
    chunk_begin_ = 0;
    chunk_end_ = 0;
    edge_num_ = 0;
    for (IdType i = 0; i < vertex_chunk_num; ++i) {
      GAR_ASSIGN_OR_RAISE_ERROR(
          edge_chunk_nums[i],
          utils::GetEdgeChunkNum(prefix, edge_info, adj_list_type_, i));
      if (i < vertex_chunk_begin) {
        chunk_begin_ += edge_chunk_nums[i];
        chunk_end_ += edge_chunk_nums[i];
      }
      if (i >= vertex_chunk_begin && i < vertex_chunk_end) {
        chunk_end_ += edge_chunk_nums[i];
        GAR_ASSIGN_OR_RAISE_ERROR(
            auto chunk_edge_num_,
            utils::GetEdgeNum(prefix, edge_info, adj_list_type_, i));
        edge_num_ += chunk_edge_num_;
      }
    }
    index_converter_ =
        std::make_shared<util::IndexConverter>(std::move(edge_chunk_nums));
  }

  /** The iterator pointing to the first edge. */
  EdgeIter begin() {
    if (begin_ == nullptr) {
      EdgeIter iter(edge_info_, prefix_, adj_list_type_, chunk_begin_, 0,
                    chunk_begin_, chunk_end_, index_converter_);
      begin_ = std::make_shared<EdgeIter>(iter);
    }
    return *begin_;
  }

  /** The iterator pointing to the past-the-end element. */
  EdgeIter end() {
    if (end_ == nullptr) {
      EdgeIter iter(edge_info_, prefix_, adj_list_type_, chunk_end_, 0,
                    chunk_begin_, chunk_end_, index_converter_);
      end_ = std::make_shared<EdgeIter>(iter);
    }
    return *end_;
  }

  /**
   * Construct and return the iterator pointing to the first out-going edge of
   * the vertex with specific id after the input iterator.
   *
   * @param id The vertex id.
   * @param from The input iterator.
   * @return The new constructed iterator.
   */
  EdgeIter find_src(IdType id, const EdgeIter& from) {
    auto result = utils::GetAdjListOffsetOfVertex(edge_info_, prefix_,
                                                  adj_list_type_, id);
    if (!result.status().ok()) {
      return this->end();
    }
    auto begin_offset = result.value().first;
    auto end_offset = result.value().second;
    if (begin_offset >= end_offset) {
      return this->end();
    }
    auto begin_global_chunk_index =
        index_converter_->IndexPairToGlobalChunkIndex(
            id / edge_info_.GetSrcChunkSize(),
            begin_offset / edge_info_.GetChunkSize());
    auto end_global_chunk_index = index_converter_->IndexPairToGlobalChunkIndex(
        id / edge_info_.GetSrcChunkSize(),
        end_offset / edge_info_.GetChunkSize());
    if (begin_global_chunk_index > from.global_chunk_index_) {
      return EdgeIter(edge_info_, prefix_, adj_list_type_,
                      begin_global_chunk_index, begin_offset, chunk_begin_,
                      chunk_end_, index_converter_);
    } else if (end_global_chunk_index < from.global_chunk_index_) {
      return this->end();
    } else {
      if (begin_offset > from.cur_offset_) {
        return EdgeIter(edge_info_, prefix_, adj_list_type_,
                        begin_global_chunk_index, begin_offset, chunk_begin_,
                        chunk_end_, index_converter_);
      } else if (end_offset <= from.cur_offset_) {
        return this->end();
      } else {
        return EdgeIter(edge_info_, prefix_, adj_list_type_,
                        from.global_chunk_index_, from.cur_offset_,
                        chunk_begin_, chunk_end_, index_converter_);
      }
    }
    return this->end();
  }

  /**
   * Construct and return the iterator pointing to the first incoming edge of
   * the vertex with specific id after the input iterator.
   *
   * @param id The vertex id.
   * @param from The input iterator.
   * @return The new constructed iterator.
   */
  EdgeIter find_dst(IdType id, const EdgeIter& from) {
    EdgeIter iter(from);
    auto end = this->end();
    while (iter != end) {
      auto edge = *iter;
      if (edge.destination() == id) {
        break;
      }
      ++iter;
    }
    return iter;
  }

  /** Get the number of edges in the collection. */
  size_t size() const noexcept { return edge_num_; }

 private:
  EdgeInfo edge_info_;
  std::string prefix_;
  IdType chunk_begin_, chunk_end_;
  std::shared_ptr<util::IndexConverter> index_converter_;
  std::shared_ptr<EdgeIter> begin_, end_;
  IdType edge_num_;
};

/**
 * @brief The implementation of EdgesCollection when the type of adjList is
 * AdjListType::ordered_by_dest.
 *
 */
template <>
class EdgesCollection<AdjListType::ordered_by_dest> {
 public:
  static const AdjListType adj_list_type_;

  /**
   * @brief Initialize the EdgesCollection with a range of chunks.
   *
   * @param edge_info The edge info that describes the edge type.
   * @param prefix The absolute prefix.
   * @param vertex_chunk_begin The index of the begin vertex chunk.
   * @param vertex_chunk_end The index of the end vertex chunk (not included).
   */
  EdgesCollection(const EdgeInfo& edge_info, const std::string& prefix,
                  IdType vertex_chunk_begin = 0,
                  IdType vertex_chunk_end = std::numeric_limits<int64_t>::max())
      : edge_info_(edge_info), prefix_(prefix) {
    GAR_ASSIGN_OR_RAISE_ERROR(
        auto vertex_chunk_num,
        utils::GetVertexChunkNum(prefix_, edge_info_, adj_list_type_));
    std::vector<IdType> edge_chunk_nums(vertex_chunk_num, 0);
    if (vertex_chunk_end == std::numeric_limits<int64_t>::max()) {
      vertex_chunk_end = vertex_chunk_num;
    }
    chunk_begin_ = 0;
    chunk_end_ = 0;
    edge_num_ = 0;
    for (IdType i = 0; i < vertex_chunk_num; ++i) {
      GAR_ASSIGN_OR_RAISE_ERROR(
          edge_chunk_nums[i],
          utils::GetEdgeChunkNum(prefix, edge_info, adj_list_type_, i));
      if (i < vertex_chunk_begin) {
        chunk_begin_ += edge_chunk_nums[i];
        chunk_end_ += edge_chunk_nums[i];
      }
      if (i >= vertex_chunk_begin && i < vertex_chunk_end) {
        chunk_end_ += edge_chunk_nums[i];
        GAR_ASSIGN_OR_RAISE_ERROR(
            auto chunk_edge_num_,
            utils::GetEdgeNum(prefix, edge_info, adj_list_type_, i));
        edge_num_ += chunk_edge_num_;
      }
    }
    index_converter_ =
        std::make_shared<util::IndexConverter>(std::move(edge_chunk_nums));
  }

  /** The iterator pointing to the first edge. */
  EdgeIter begin() {
    if (begin_ == nullptr) {
      EdgeIter iter(edge_info_, prefix_, adj_list_type_, chunk_begin_, 0,
                    chunk_begin_, chunk_end_, index_converter_);
      begin_ = std::make_shared<EdgeIter>(iter);
    }
    return *begin_;
  }

  /** The iterator pointing to the past-the-end element. */
  EdgeIter end() {
    if (end_ == nullptr) {
      EdgeIter iter(edge_info_, prefix_, adj_list_type_, chunk_end_, 0,
                    chunk_begin_, chunk_end_, index_converter_);
      end_ = std::make_shared<EdgeIter>(iter);
    }
    return *end_;
  }

  /**
   * Construct and return the iterator pointing to the first out-going edge of
   * the vertex with specific id after the input iterator.
   *
   * @param id The vertex id.
   * @param from The input iterator.
   * @return The new constructed iterator.
   */
  EdgeIter find_src(IdType id, const EdgeIter& from) {
    EdgeIter iter(from);
    auto end = this->end();
    while (iter != end) {
      auto edge = *iter;
      if (edge.source() == id) {
        break;
      }
      ++iter;
    }
    return iter;
  }

  /**
   * Construct and return the iterator pointing to the first incoming edge of
   * the vertex with specific id after the input iterator.
   *
   * @param id The vertex id.
   * @param from The input iterator.
   * @return The new constructed iterator.
   */
  EdgeIter find_dst(IdType id, const EdgeIter& from) {
    auto result = utils::GetAdjListOffsetOfVertex(edge_info_, prefix_,
                                                  adj_list_type_, id);
    if (!result.status().ok()) {
      return this->end();
    }
    auto begin_offset = result.value().first;
    auto end_offset = result.value().second;
    if (begin_offset >= end_offset) {
      return this->end();
    }
    auto begin_global_chunk_index =
        index_converter_->IndexPairToGlobalChunkIndex(
            id / edge_info_.GetDstChunkSize(),
            begin_offset / edge_info_.GetChunkSize());
    auto end_global_chunk_index = index_converter_->IndexPairToGlobalChunkIndex(
        id / edge_info_.GetDstChunkSize(),
        end_offset / edge_info_.GetChunkSize());
    if (begin_global_chunk_index > from.global_chunk_index_) {
      return EdgeIter(edge_info_, prefix_, adj_list_type_,
                      begin_global_chunk_index, begin_offset, chunk_begin_,
                      chunk_end_, index_converter_);
    } else if (end_global_chunk_index < from.global_chunk_index_) {
      return this->end();
    } else {
      if (begin_offset >= from.cur_offset_) {
        return EdgeIter(edge_info_, prefix_, adj_list_type_,
                        begin_global_chunk_index, begin_offset, chunk_begin_,
                        chunk_end_, index_converter_);
      } else if (end_offset <= from.cur_offset_) {
        return this->end();
      } else {
        return EdgeIter(edge_info_, prefix_, adj_list_type_,
                        from.global_chunk_index_, from.cur_offset_,
                        chunk_begin_, chunk_end_, index_converter_);
      }
    }
    return this->end();
  }

  /** Get the number of edges in the collection. */
  size_t size() const noexcept { return edge_num_; }

 private:
  EdgeInfo edge_info_;
  std::string prefix_;
  IdType chunk_begin_, chunk_end_;
  std::shared_ptr<util::IndexConverter> index_converter_;
  std::shared_ptr<EdgeIter> begin_, end_;
  IdType edge_num_;
};

/**
 * @brief The implementation of EdgesCollection when the type of adjList is
 * AdjListType::unordered_by_source.
 *
 */
template <>
class EdgesCollection<AdjListType::unordered_by_source> {
 public:
  static const AdjListType adj_list_type_;

  /**
   * @brief Initialize the EdgesCollection with a range of chunks.
   *
   * @param edge_info The edge info that describes the edge type.
   * @param prefix The absolute prefix.
   * @param vertex_chunk_begin The index of the begin vertex chunk.
   * @param vertex_chunk_end The index of the end vertex chunk (not included).
   */
  EdgesCollection(const EdgeInfo& edge_info, const std::string& prefix,
                  IdType vertex_chunk_begin = 0,
                  IdType vertex_chunk_end = std::numeric_limits<int64_t>::max())
      : edge_info_(edge_info), prefix_(prefix) {
    GAR_ASSIGN_OR_RAISE_ERROR(
        auto vertex_chunk_num,
        utils::GetVertexChunkNum(prefix_, edge_info_, adj_list_type_));
    std::vector<IdType> edge_chunk_nums(vertex_chunk_num, 0);
    if (vertex_chunk_end == std::numeric_limits<int64_t>::max()) {
      vertex_chunk_end = vertex_chunk_num;
    }
    chunk_begin_ = 0;
    chunk_end_ = 0;
    edge_num_ = 0;
    for (IdType i = 0; i < vertex_chunk_num; ++i) {
      GAR_ASSIGN_OR_RAISE_ERROR(
          edge_chunk_nums[i],
          utils::GetEdgeChunkNum(prefix, edge_info, adj_list_type_, i));
      if (i < vertex_chunk_begin) {
        chunk_begin_ += edge_chunk_nums[i];
        chunk_end_ += edge_chunk_nums[i];
      }
      if (i >= vertex_chunk_begin && i < vertex_chunk_end) {
        chunk_end_ += edge_chunk_nums[i];
        GAR_ASSIGN_OR_RAISE_ERROR(
            auto chunk_edge_num_,
            utils::GetEdgeNum(prefix, edge_info, adj_list_type_, i));
        edge_num_ += chunk_edge_num_;
      }
    }
    index_converter_ =
        std::make_shared<util::IndexConverter>(std::move(edge_chunk_nums));
  }

  /** The iterator pointing to the first edge. */
  EdgeIter begin() {
    if (begin_ == nullptr) {
      EdgeIter iter(edge_info_, prefix_, adj_list_type_, chunk_begin_, 0,
                    chunk_begin_, chunk_end_, index_converter_);
      begin_ = std::make_shared<EdgeIter>(iter);
    }
    return *begin_;
  }

  /** The iterator pointing to the past-the-end element. */
  EdgeIter end() {
    if (end_ == nullptr) {
      EdgeIter iter(edge_info_, prefix_, adj_list_type_, chunk_end_, 0,
                    chunk_begin_, chunk_end_, index_converter_);
      end_ = std::make_shared<EdgeIter>(iter);
    }
    return *end_;
  }

  /**
   * Construct and return the iterator pointing to the first out-going edge of
   * the vertex with specific id after the input iterator.
   *
   * @param id The vertex id.
   * @param from The input iterator.
   * @return The new constructed iterator.
   */
  EdgeIter find_src(IdType id, const EdgeIter& from) {
    EdgeIter iter(from);
    auto end = this->end();
    while (iter != end) {
      auto edge = *iter;
      if (edge.source() == id) {
        break;
      }
      ++iter;
    }
    return iter;
  }

  /**
   * Construct and return the iterator pointing to the first incoming edge of
   * the vertex with specific id after the input iterator.
   *
   * @param id The vertex id.
   * @param from The input iterator.
   * @return The new constructed iterator.
   */
  EdgeIter find_dst(IdType id, const EdgeIter& from) {
    EdgeIter iter(from);
    auto end = this->end();
    while (iter != end) {
      auto edge = *iter;
      if (edge.destination() == id) {
        break;
      }
      ++iter;
    }
    return iter;
  }

  /** Get the number of edges in the collection. */
  size_t size() const noexcept { return edge_num_; }

 private:
  EdgeInfo edge_info_;
  std::string prefix_;
  IdType chunk_begin_, chunk_end_;
  std::shared_ptr<util::IndexConverter> index_converter_;
  std::shared_ptr<EdgeIter> begin_, end_;
  IdType edge_num_;
};

/**
 * @brief The implementation of EdgesCollection when the type of adjList is
 * AdjListType::unordered_by_dest.
 *
 */
template <>
class EdgesCollection<AdjListType::unordered_by_dest> {
 public:
  static const AdjListType adj_list_type_;

  /**
   * @brief Initialize the EdgesCollection with a range of chunks.
   *
   * @param edge_info The edge info that describes the edge type.
   * @param prefix The absolute prefix.
   * @param vertex_chunk_begin The index of the begin vertex chunk.
   * @param vertex_chunk_end The index of the end vertex chunk (not included).
   */
  EdgesCollection(const EdgeInfo& edge_info, const std::string& prefix,
                  IdType vertex_chunk_begin = 0,
                  IdType vertex_chunk_end = std::numeric_limits<int64_t>::max())
      : edge_info_(edge_info), prefix_(prefix) {
    GAR_ASSIGN_OR_RAISE_ERROR(
        auto vertex_chunk_num,
        utils::GetVertexChunkNum(prefix_, edge_info_, adj_list_type_));
    std::vector<IdType> edge_chunk_nums(vertex_chunk_num, 0);
    if (vertex_chunk_end == std::numeric_limits<int64_t>::max()) {
      vertex_chunk_end = vertex_chunk_num;
    }
    chunk_begin_ = 0;
    chunk_end_ = 0;
    edge_num_ = 0;
    for (IdType i = 0; i < vertex_chunk_num; ++i) {
      GAR_ASSIGN_OR_RAISE_ERROR(
          edge_chunk_nums[i],
          utils::GetEdgeChunkNum(prefix, edge_info, adj_list_type_, i));
      if (i < vertex_chunk_begin) {
        chunk_begin_ += edge_chunk_nums[i];
        chunk_end_ += edge_chunk_nums[i];
      }
      if (i >= vertex_chunk_begin && i < vertex_chunk_end) {
        chunk_end_ += edge_chunk_nums[i];
        GAR_ASSIGN_OR_RAISE_ERROR(
            auto chunk_edge_num_,
            utils::GetEdgeNum(prefix, edge_info, adj_list_type_, i));
        edge_num_ += chunk_edge_num_;
      }
    }
    index_converter_ =
        std::make_shared<util::IndexConverter>(std::move(edge_chunk_nums));
  }

  /** The iterator pointing to the first edge. */
  EdgeIter begin() {
    if (begin_ == nullptr) {
      EdgeIter iter(edge_info_, prefix_, adj_list_type_, chunk_begin_, 0,
                    chunk_begin_, chunk_end_, index_converter_);
      begin_ = std::make_shared<EdgeIter>(iter);
    }
    return *begin_;
  }

  /** The iterator pointing to the past-the-end element. */
  EdgeIter end() {
    if (end_ == nullptr) {
      EdgeIter iter(edge_info_, prefix_, adj_list_type_, chunk_end_, 0,
                    chunk_begin_, chunk_end_, index_converter_);
      end_ = std::make_shared<EdgeIter>(iter);
    }
    return *end_;
  }

  /**
   * Construct and return the iterator pointing to the first out-going edge of
   * the vertex with specific id after the input iterator.
   *
   * @param id The vertex id.
   * @param from The input iterator.
   * @return The new constructed iterator.
   */
  EdgeIter find_src(IdType id, const EdgeIter& from) {
    EdgeIter iter(from);
    auto end = this->end();
    while (iter != end) {
      auto edge = *iter;
      if (edge.source() == id) {
        break;
      }
      ++iter;
    }
    return iter;
  }

  /**
   * Construct and return the iterator pointing to the first incoming edge of
   * the vertex with specific id after the input iterator.
   *
   * @param id The vertex id.
   * @param from The input iterator.
   * @return The new constructed iterator.
   */
  EdgeIter find_dst(IdType id, const EdgeIter& from) {
    EdgeIter iter(from);
    auto end = this->end();
    while (iter != end) {
      auto edge = *iter;
      if (edge.destination() == id) {
        break;
      }
      ++iter;
    }
    return iter;
  }

  /** Get the number of edges in the collection. */
  size_t size() const noexcept { return edge_num_; }

 private:
  EdgeInfo edge_info_;
  std::string prefix_;
  IdType chunk_begin_, chunk_end_;
  std::shared_ptr<util::IndexConverter> index_converter_;
  std::shared_ptr<EdgeIter> begin_, end_;
  IdType edge_num_;
};

typedef std::variant<EdgesCollection<AdjListType::ordered_by_source>,
                     EdgesCollection<AdjListType::ordered_by_dest>,
                     EdgesCollection<AdjListType::unordered_by_source>,
                     EdgesCollection<AdjListType::unordered_by_dest>>
    Edges;

/**
 * @brief Construct the collection for vertices with specific label.
 *
 * @param graph_info The GraphInfo for the graph.
 * @param label The vertex label.
 * @return The constructed collection or error.
 */
static inline Result<VerticesCollection> ConstructVerticesCollection(
    const GraphInfo& graph_info, const std::string& label) noexcept {
  VertexInfo vertex_info;
  GAR_ASSIGN_OR_RAISE(vertex_info, graph_info.GetVertexInfo(label));
  return VerticesCollection(vertex_info, graph_info.GetPrefix());
}

/**
 * @brief Construct the collection for a range of edges.
 *
 * @param graph_info The GraphInfo for the graph.
 * @param src_label The source vertex label.
 * @param edge_label The edge label.
 * @param dst_label The destination vertex label.
 * @param adj_list_type The adjList type.
 * @param vertex_chunk_begin The index of the begin vertex chunk.
 * @param vertex_chunk_end The index of the end vertex chunk (not included).
 * @return The constructed collection or error.
 */
static inline Result<Edges> ConstructEdgesCollection(
    const GraphInfo& graph_info, const std::string& src_label,
    const std::string& edge_label, const std::string& dst_label,
    AdjListType adj_list_type, const IdType vertex_chunk_begin = 0,
    const IdType vertex_chunk_end =
        std::numeric_limits<int64_t>::max()) noexcept {
  EdgeInfo edge_info;
  GAR_ASSIGN_OR_RAISE(edge_info,
                      graph_info.GetEdgeInfo(src_label, edge_label, dst_label));
  if (!edge_info.ContainAdjList(adj_list_type)) {
    return Status::Invalid("Invalid adj list type");
  }
  switch (adj_list_type) {
  case AdjListType::ordered_by_source:
    return EdgesCollection<AdjListType::ordered_by_source>(
        edge_info, graph_info.GetPrefix(), vertex_chunk_begin,
        vertex_chunk_end);
  case AdjListType::ordered_by_dest:
    return EdgesCollection<AdjListType::ordered_by_dest>(
        edge_info, graph_info.GetPrefix(), vertex_chunk_begin,
        vertex_chunk_end);
  case AdjListType::unordered_by_source:
    return EdgesCollection<AdjListType::unordered_by_source>(
        edge_info, graph_info.GetPrefix(), vertex_chunk_begin,
        vertex_chunk_end);
  case AdjListType::unordered_by_dest:
    return EdgesCollection<AdjListType::unordered_by_dest>(
        edge_info, graph_info.GetPrefix(), vertex_chunk_begin,
        vertex_chunk_end);
  default:
    return Status::Invalid("Invalid adj list type");
  }
  return Status::Invalid("Invalid adj list type");
}
}  // namespace GAR_NAMESPACE_INTERNAL

#endif  // GAR_GRAPH_H_
